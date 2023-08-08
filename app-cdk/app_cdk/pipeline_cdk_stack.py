import os
from constructs import Construct
from aws_cdk import (
    Stack,
    CfnOutput,
    aws_codecommit as codecommit,
    aws_codepipeline as codepipeline,
    aws_codebuild as codebuild,
    aws_codepipeline_actions as codepipeline_actions,
    aws_iam as iam
)


class PipelineCdkStack(Stack):

    def __init__(self, scope: Construct, id: str, ecr_repository, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Pipeline code will go here
        repo = codecommit.Repository(
            self, 'Cross_Border_CICD',
            repository_name='Cross_Border_CICD',
            description='Repository for my application code and infrastructure'
        )

        pipeline = codepipeline.Pipeline(
            self, "CICD_Pipeline",
            cross_account_keys=False
        )

        code_quality_build = codebuild.PipelineProject(
            self, "Code Quality",
            build_spec=codebuild.BuildSpec.from_source_filename("./buildspec_test.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.LARGE,
            ),
        )

        docker_build_project = codebuild.PipelineProject(
            self, "Docker Push ECR",
            build_spec=codebuild.BuildSpec.from_source_filename("./buildspec_docker.yml"),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True,
                compute_type=codebuild.ComputeType.LARGE,
                environment_variables={
                    "IMAGE_TAG": codebuild.BuildEnvironmentVariable(
                        type=codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                        value='latest'
                    ),
                    "IMAGE_REPO_URI": codebuild.BuildEnvironmentVariable(
                        type=codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                        value=ecr_repository.repository_uri
                    ),
                    "AWS_DEFAULT_REGION": codebuild.BuildEnvironmentVariable(
                        type=codebuild.BuildEnvironmentVariableType.PLAINTEXT,
                        value=os.environ["CDK_DEFAULT_REGION"]
                    )
                }
            ),
        )

        docker_build_project.add_to_role_policy(iam.PolicyStatement(
            effect=iam.Effect.ALLOW,
            actions=[
                "ecr:GetAuthorizationToken",
                "ecr:BatchCheckLayerAvailability",
                "ecr:GetDownloadUrlForLayer",
                "ecr:GetRepositoryPolicy",
                "ecr:DescribeRepositories",
                "ecr:ListImages",
                "ecr:DescribeImages",
                "ecr:BatchGetImage",
                "ecr:InitiateLayerUpload",
                "ecr:UploadLayerPart",
                "ecr:CompleteLayerUpload",
                "ecr:PutImage"
            ],
            resources=['*'],
        ))

        source_output = codepipeline.Artifact()
        unit_test_output = codepipeline.Artifact()
        docker_build_output = codepipeline.Artifact()

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
            project=code_quality_build,
            input=source_output,
            outputs=[unit_test_output]
        )

        pipeline.add_stage(
            stage_name="Code-Quality-Testing",
            actions=[build_action]
        )

        docker_build_action = codepipeline_actions.CodeBuildAction(
            action_name="Docker-Build",
            project=docker_build_project,
            input=source_output,
            outputs=[docker_build_output]
        )

        pipeline.add_stage(
            stage_name="Docker-Build",
            actions=[docker_build_action]
        )

        CfnOutput(
            self, 'CodeCommitRepositoryUrl',
            value=repo.repository_clone_url_http
        )
