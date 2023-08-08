from aws_cdk import (
    Stack,
    aws_ec2 as ec2,
    aws_s3 as s3,
    aws_ssm as ssm,
    aws_iam as iam,
    aws_eks as eks
)
from constructs import Construct


class EKSStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, vpc: ec2.Vpc, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # The code that defines your stack goes here
        env_name = self.node.try_get_context("env")
        eks_role = iam.Role(self, "eksadmin", assumed_by=iam.ServicePrincipal(service='ec2.amazonaws.com'),
                            role_name='eks-cluster-role', managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name='AdministratorAccess')])
        eks_instance_profile = iam.CfnInstanceProfile(self, 'instanceprofile',
                                                      roles=[
                                                          eks_role.role_name],
                                                      instance_profile_name='eks-cluster-role')

        cluster = eks.Cluster(self, 'prod', cluster_name='cb_devops',
                              version=eks.KubernetesVersion.V1_24,
                              vpc=vpc,
                              vpc_subnets=[ec2.SubnetSelection(
                                  subnet_type=ec2.SubnetType.PRIVATE_ISOLATED)],
                              default_capacity=0,
                              masters_role=eks_role)

        nodegroup = cluster.add_nodegroup_capacity('eks-nodegroup',
                                                   instance_types=[ec2.InstanceType('t3.micro')],
                                                   disk_size=50,
                                                   min_size=1,
                                                   max_size=2,
                                                   desired_size=1,
                                                   subnets=ec2.SubnetSelection(
                                                       subnet_type=ec2.SubnetType.PRIVATE_ISOLATED),
                                                   capacity_type=eks.CapacityType.ON_DEMAND)
