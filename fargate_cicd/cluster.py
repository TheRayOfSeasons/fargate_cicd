from aws_cdk import core
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecr as ecr
from aws_cdk import aws_ecs as ecs


class Cluster(core.Construct):
    """
    ECS cluster for our application.
    """

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs):
        super().__init__(scope, construct_id)
        vpc = ec2.Vpc(self, 'sample-fargate-vpc', max_azs=2)
        self.ecsCluster = ecs.Cluster(self, 'sample-ecs-cluster', vpc=vpc)
        self.output()

    def output(self):
        """
        Build cloudformation generated from this construct.
        """
        core.CfnOutput(self, 'ECSClusterARN', value=self.ecsCluster.cluster_arn)
