from aws_cdk import core
from aws_cdk import aws_codebuild as codebuild
from aws_cdk import aws_codepipeline as codepipeline
from aws_cdk import aws_codepipeline_actions as codepipeline_actions
from aws_cdk import aws_ssm as ssm
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs

from .webapp import WebApp


class Pipeline(core.Construct):
    """
    A construct that defines the deployment
    pipeline and CICD configurations.
    """

    def __init__(
            self, scope: core.Construct, construct_id: str,
            webapp: WebApp, **kwargs):
        super().__init__(scope, construct_id)
        self.webapp = webapp
        self.service = webapp.service
        self.ecr_repo = webapp.ecr_repo
        self.container_name = webapp.container_name

        self.pipeline = self._create_pipeline()

    def _create_pipeline(self) -> codepipeline.Pipeline:
        """
        Define and apply the specifications on how
        the deployment process will go.
        """
        source_output = codepipeline.Artifact()
        build_output = codepipeline.Artifact()
        return codepipeline.Pipeline(
            self,
            'Pipeline',
            stages=[
                self._create_source_stage('Source', source_output),
                self._create_image_build_stage(
                    'Build', source_output, build_output),
                self._create_deploy_stage('Deploy', build_output)
            ]
        )

    def _create_source_stage(
            self, stage_name: str, output: codepipeline.Artifact):
        """
        A pipeline stage that is responsible
        with fetching the application from
        GitHub.
        """
        secret_token = (
            core
            .SecretValue
            .secrets_manager('/fargate_cicd_staging/dev/GITHUB_TOKEN')
        )
        repo = (
            ssm
            .StringParameter
            .value_for_string_parameter(
                self,
                '/fargate_cicd_staging/dev/GITHUB_REPO'
            )
        )
        owner = (
            ssm
            .StringParameter
            .value_for_string_parameter(
                self,
                '/fargate_cicd_staging/dev/GITHUB_OWNER'
            )
        )
        github_action = codepipeline_actions.GitHubSourceAction(
            action_name='Github_Source',
            owner=owner,
            repo=repo,
            oauth_token=secret_token,
            output=output
        )
        return {
            'stage_name': stage_name,
            'actions': [github_action]
        }

    def _create_image_build_stage(
            self, stage_name: str,
            input: codepipeline.Artifact,
            output: codepipeline.Artifact):
        """
        A pipeline stage that is responsible
        with building the application.
        """
        project = codebuild.PipelineProject(
            self,
            'Project',
            build_spec=self._create_build_spec(),
            environment={
                'buildImage': codebuild.LinuxBuildImage.STANDARD_2_0,
                'priveledged': True
            },
            environment_variables={
                'REPOSITORY_URI': {'value': self.ecr_repo.repository_uri},
                'CONTAINER_NAME': {'value': self.container_name}
            }
        )
        self.ecr_repo.grant_pull_push(project.grant_principal)

        codebuild_action = codepipeline_actions.CodeBuildAction(
            action_name='CodeBuild_Action',
            input=input,
            outputs=[output],
            project=project
        )
        return {
            'stageName': stage_name,
            'actions': [codebuild_action]
        }

    def _create_deploy_stage(
            self, stage_name: str, input: codepipeline.Artifact):
        """
        A pipeline stage that will finally
        deploy the application container
        into our ECS Fargate service.
        """
        ecs_deploy_action = codepipeline_actions.EcsDeployAction(
            action_name='ECSDeploy_Action',
            input=input,
            service=self.service,
        )
        return {
            'stageName': stage_name,
            'actions': [ecs_deploy_action]
        }

    def _create_build_spec(self) -> codebuild.BuildSpec:
        """
        Define the build specifications.
        """
        return codebuild.BuildSpec.from_object({
            'version': '0.2',
            'phases': {
                'install': {
                    'runtime-versions': {
                        'python': '3.8'
                    }
                },
                'commands': [
                    'pip install -r requirements.txt'
                ]
            },
            'pre_build': {
                'commands': [
                    'aws --version',
                    '$(aws ecr get-login --region ${AWS_DEFAULT_REGION} --no-include-email | sed \'s|https://[]\)',
                    'COMMIT_HASH=${echo $CODEBUILD_RESOLVED_RESOURCE_VERSION | cut 1-7}',
                    'IMAGE_TAG=${COMMIT_HASH:=latest}'
                ]
            },
            'build': {
                'commands': [
                    'docker build -t $REPOSITORY_URI:latest',
                    'docker tag $REPOSITORY_URI:latest $REPOSITORY_URI:$IMAGE_TAG'
                ]
            },
            'post_build': {
                'commands': [
                    'docker push $REPOSITORY_URI:latest',
                    'docker push $REPOSITORY_URI:$IMAGE_TAG',
                    'printf "[{\\"name\\": \\"${CONTAINER_NAME}\\", \\"${imageUri}\\": \\"${REPOSITORY_URI}:latest\\"}]" > imagedefinitions.json'
                ]
            },
            'artifacts': {
                'files': [
                    'imagedefinitions.json'
                ]
            }
        })

    def output(self):
        """
        Build cloudformation generated from this construct.
        """
        core.CfnOutput(self, 'Pipeline ARN', value=self.pipeline.pipeline_arn)
