from aws_cdk import core
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_rds as rds
from aws_cdk import aws_s3 as s3

from .cluster import Cluster


class Storage(core.Construct):
    """
    A construct that defines all the services
    responsible for storage.
    """

    def __init__(
            self, scope: core.Construct, construct_id: id,
            cluster: Cluster, **kwargs) -> None:
        super().__init__(scope, construct_id)
        self.rds_database = self._create_RDS(cluster=cluster)
        self.buckets = self._create_buckets()
        self.output()

    def _create_RDS(self, cluster: Cluster) -> rds.DatabaseInstance:
        """
        Define an RDS instance running with a PostgreSQL engine.
        """
        version = rds.PostgresEngineVersion.VER_12_4
        engine = rds.DatabaseInstanceEngine.postgres(version=version)
        database = rds.DatabaseInstance(
            self,
            'postgresql_database',
            engine=engine,
            allocated_storage=20, # 20 GB
            max_allocated_storage=100, # 100 GB
            vpc=cluster.ecsCluster.vpc,
            multi_az=True
        )
        return database

    def _create_buckets(self) -> dict:
        """
        Define S3 buckets.
        """
        static_bucket = s3.Bucket(
            self,
            'static_bucket',
            bucket_name='fargate-cicd-test-static-bucket',
            removal_policy=core.RemovalPolicy.DESTROY
        )
        media_bucket = s3.Bucket(
            self,
            'media_bucket',
            bucket_name='fargate-cicd-test-media-bucket',
            removal_policy=core.RemovalPolicy.DESTROY
        )
        buckets = {
            'static': static_bucket,
            'media': media_bucket
        }
        return buckets

    def output(self):
        """
        Build cloudformation generated from this construct.
        """
        core.CfnOutput(
            self,
            'RDS_Database',
            value=self.rds_database.instance_arn
        )
        for key, bucket in self.buckets.items():
            bucket_identifier = f'{key.upper()}_S3_Bucket'
            core.CfnOutput(self, bucket_identifier, value=bucket.bucket_arn)
