#!/usr/bin/env python3

from aws_cdk import core

from fargate_cicd.fargate_cicd_stack import FargateCicdStack


app = core.App()
FargateCicdStack(app, "fargate-cicd")

app.synth()
