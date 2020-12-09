from aws_cdk import core

from .cluster import Cluster
from .pipeline import Pipeline
from .storage import Storage
from .webapp import WebApp


class FargateCicdStack(core.Stack):
    """
    A stack for deploying up a dockerized Django application
    in ECS through Fargate with a full CICD pipeline.
    """

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        cluster = Cluster(self, 'Cluster')
        storage = Storage(self, 'Storage', cluster=cluster)
        webapp = WebApp(self, 'WebApp', cluster=cluster, storage=storage)
        pipeline = Pipeline(self, 'Pipeline', webapp=webapp)
