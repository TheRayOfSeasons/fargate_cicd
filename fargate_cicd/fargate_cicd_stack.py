from aws_cdk import core
from aws_cdk import aws_ec2 as ec2
from aws_cdk import aws_ecs as ecs
from aws_cdk import aws_elasticloadbalancingv2 as elbv2
from aws_cdk import aws_route53 as route53


class FargateCicdStack(core.Stack):
    """
    A stack for deploying up a dockerized Django application
    in ECS through Fargate with a full CICD pipeline.
    """

    def __init__(self, scope: core.Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.vpc = ec2.Vpc(self, 'sample-fargate-vpc', max_azs=2)
        self.roles = self.define_iam_roles()
        self.DNS_router = self.define_DNS_router()
        self.fargate_service = self.define_ecs_service()

    def define_iam_roles(self) -> dict:
        """
        Defines the iam roles for this stack.
        """
        roles = {

        }
        return roles

    def define_DNS_router(self) -> route53.PublicHostedZone:
        """
        Defines all routers and gateways
        for public access of the application.
        """
        router = route53.PublicHostedZone(
            self,
            'sample-route-53',
            zone_name='app.therayofseasons.fargatestack'
        )
        return router

    def define_ecs_service(self):
        """
        Defines all the necessary services for
        pulling and running the application in
        ECS Fargate.
        """
        cluster = ecs.Cluster(self, 'sample-ecs-cluster', vpc=self.vpc)

        load_balancer = elbv2.ApplicationLoadBalancer(
            self,
            'sample-load-balancer',
            vpc=self.vpc,
            internet_facing=True
        )

        load_balanced_listener = load_balancer.add_listener(
            'PublicListener',
            port=80,
            open=True
        )

        load_balanced_listener.add_target_groups(
            'default',
            target_groups=[
                elbv2.ApplicationTargetGroup(
                    self,
                    'default',
                    vpc=self.vpc,
                    protocol=elbv2.ApplicationProtocol.HTTP,
                    port=80
                ),
            ]
        )

        core.CfnOutput(
            self,
            'LoadBalancerDNS',
            value=load_balancer.load_balancer_dns_name
        )

        task_definition = ecs.FargateTaskDefinition(
            self,
            'sample-fargate-task-definition'
        )

        container = task_definition.add_container(
            'web',
            image=ecs.ContainerImage.from_asset('./web'),
            memory_limit_mib=256
        )
        port_mapping = ecs.PortMapping(
            container_port=80,
            protocol=ecs.Protocol.TCP
        )
        container.add_port_mappings(port_mapping)

        fargate_service = ecs.FargateService(
            self,
            'fargate-service',
            cluster=cluster,
            desired_count=3,
            task_definition=task_definition,
            max_healthy_percent=200,
            min_healthy_percent=100,
            # No need for a public IP since we have a NAT Gateway in this VPC.
            assign_public_ip=False
        )

        health_check = elbv2.HealthCheck(
            healthy_threshold_count=2,
            interval=core.Duration.seconds(60),
            timeout=core.Duration.seconds(5),
        )

        load_balanced_listener.add_targets(
            'target-fargate-service',
            port=80,
            path_pattern='*',
            priority=2,
            health_check=health_check,
            # Drain containers for 10 seconds when stopping.
            deregistration_delay=core.Duration.seconds(10),
            targets=[fargate_service],
        )
        return fargate_service
