from constructs import Construct
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_codecommit as codecommit,
)


class PipelineCdkStack(Stack):

    def __init__(self, scope: Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Creates a CodeCommit repository called 'CICD_Sample'
        repo = codecommit.Repository(
            self, 'CICD_Sample',
            repository_name='CICD_Sample',
            description='Repository for my application code and infrastructure'
        )

        CfnOutput(
            self, 'CodeCommitRepositoryUrl',
            value=repo.repository_clone_url_http
        )
