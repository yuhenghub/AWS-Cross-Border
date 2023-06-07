#!/usr/bin/env python3
import os

import aws_cdk as cdk

from app_cdk.app_cdk_stack import AppCdkStack
from app_cdk.pipeline_cdk_stack import PipelineCdkStack

app = cdk.App()
AppCdkStack(app, "AppCdkStack")
PipelineCdkStack(app, "pipeline-stack")
app.synth()
