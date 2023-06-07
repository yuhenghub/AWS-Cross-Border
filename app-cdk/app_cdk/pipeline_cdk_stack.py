from constructs import Construct
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_codecommit as codecommit,
    aws_codebuild as codebuild,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as codepipeline_actions
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
        pipeline = codepipeline.Pipeline(
            self, "CICD_Pipeline",
            cross_account_keys=False
        )

        codeQualityBuild = codebuild.PipelineProject(
            self, "Code Quality",
            build_spec=codebuild.BuildSpec.from_source_filename("./buildspec_test.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.AMAZON_LINUX_2_4,
                privileged=True,
                compute_type=codebuild.ComputeType.LARGE,
            ),
        )

        source_output = codepipeline.Artifact()
        unit_test_output = codepipeline.Artifact()

        source_action = codepipeline_actions.CodeCommitSourceAction(
            action_name="CodeCommit",
            repository=repo,
            output=source_output,
            branch="main"
        )

        pipeline.add_stage(
            stage_name="Source",
            actions=[source_action]
        )

        build_action = codepipeline_actions.CodeBuildAction(
            action_name="Unit-Test",
            project=codeQualityBuild,
            # The build action must use the CodeCommitSourceAction output as input.
            input=source_output,
            outputs=[unit_test_output]
        )

        pipeline.add_stage(
            stage_name="Code-Quality-Testing",
            actions=[build_action]
        )
        
        CfnOutput(
            self, 'CodeCommitRepositoryUrl',
            value=repo.repository_clone_url_http
        )
