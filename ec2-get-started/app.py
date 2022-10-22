from aws_cdk import (
    core,
    aws_ec2 as ec2,
)
import os

class MyFirstEc2(core.Stack):
    def __init__(self, scope: core.App, name: str, key_name: str, **kwargs) -> None:
        super().__init__(scope, name, **kwargs)

        # <1>
        # VPCを定義
        vpc = ec2.Vpc(
            self, "MyFirstEc2-Vpc",
            max_azs=1,                        # avaialibility zone(AZ)を設定.　
            cidr="10.10.0.0/23",              # VPC内のIPv4レンジを指定. 10.10.0.0/23は10.10.0.0から10.10.1.255までの512個の連続したアドレス範囲を指定している。
            subnet_configuration=[            # VPCにどのようなサブネットを作るかを決めている。サブネットの種類にはprivateとpublicの2種類がある。
                ec2.SubnetConfiguration(
                    name="public",
                    subnet_type=ec2.SubnetType.PUBLIC,
                )
            ],
            nat_gateways=0,
        )

        # <2>
        # security group(SG)を定義. ここでは任意のIPv4のアドレスからの、ポート22への接続を許可している. それ以外の接続は拒絶される.
        sg = ec2.SecurityGroup(
            self, "MyFirstEc2Vpc-Sg",
            vpc=vpc,
            allow_all_outbound=True,
        )
        sg.add_ingress_rule(
            peer=ec2.Peer.any_ipv4(),
            connection=ec2.Port.tcp(22),
        )

        # <3>
        # 上で作ったVPCとSGが付与されたEC2インスタンスを作成している.インスタンスタイプは "t2.micro" を選択し "Amazon Linux" をOSとして設定している.
        host = ec2.Instance(
            self, "MyFirstEc2Instance",
            instance_type=ec2.InstanceType("t2.micro"),
            machine_image=ec2.MachineImage.latest_amazon_linux(),
            vpc=vpc,
            vpc_subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC),
            security_group=sg,
            key_name=key_name
        )

        # print the server address
        core.CfnOutput(self, "InstancePublicDnsName", value=host.instance_public_dns_name)
        core.CfnOutput(self, "InstancePublicIp", value=host.instance_public_ip)

app = core.App()

MyFirstEc2(
    app, "MyFirstEc2",
    key_name=app.node.try_get_context("key_name"),
    env={
        "region": os.environ["CDK_DEFAULT_REGION"],
        "account": os.environ["CDK_DEFAULT_ACCOUNT"],
    }
)

app.synth()
