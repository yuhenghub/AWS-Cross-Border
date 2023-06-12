#!/usr/bin/env python3
import aws_cdk as cdk

from app_cdk.app_cdk_stack import AppCdkStack
from app_cdk.pipeline_cdk_stack import PipelineCdkStack
from app_cdk.ecr_cdk_stack import EcrCdkStack

app = cdk.App()
AppCdkStack(app, "app-cdk-stack")

ecr_stack = EcrCdkStack(app, 'ecr-stack')

PipelineCdkStack(
    app,
    "pipeline-stack",
    ecr_repository=ecr_stack.ecr_data
)

app.synth()
