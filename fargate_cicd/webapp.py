from aws_cdk import core
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_ecs_patterns as ecs_patterns

from .cluster import Cluster


class WebApp(core.Construct):
    """
    Our application construct.
    """

    def __init__(
            self, scope: core.Construct, construct_id: str,
            cluster: Cluster, **kwargs):
        super().__init__(scope, construct_id)
        self.fargate_service = self._create_service(cluster)
        self.ecr_repo = self._create_ecr_repository()
        self.ecr_repo.grant_pull(
            self.fargate_service.task_definition.execution_role)
        self.service = self.fargate_service.service
        self.container_name = (
            self
            .fargate_service
            .task_definition
            .default_container
            .container_name
        )

        self._add_auto_scaling()
        self.output()

    def _create_service(self, cluster: ecs.Cluster):
        """
        This defines and creates the services where
        our web application will be deployed in.
        """
        return ecs_patterns.ApplicationLoadBalancedFargateService(
            self,
            'Service',
            vpc=cluster.ecsCluster.vpc,
            task_image_options={
                'image': ecs.ContainerImage.from_asset('./web')
            }
        )

    def _create_ecr_repository(self):
        """
        This defines and creates an ECR repository
        where our docker image and containers will
        be stored.
        """
        return ecr.Repository(self, 'ECRRepo')

    def _add_auto_scaling(self):
        """
        Configure and add how our application
        service will automatically scale.
        """
        auto_scaling_group = self.fargate_service.service.auto_scale_task_count(
            min_capacity=2,
            max_capacity=10
        )
        auto_scaling_group.scale_on_cpu_utilization(
            'CpuScaling',
            target_utilization_percent=50,
            scale_in_cooldown=core.Duration.seconds(60),
            scale_out_cooldown=core.Duration.seconds(60)
        )

    def output(self):
        """
        Build cloudformation generated from this construct.
        """
        core.CfnOutput(self, 'ECRRepo_ARN', value=self.ecr_repo.repository_arn)
        core.CfnOutput(self, 'ContainerName', value=self.container_name)
