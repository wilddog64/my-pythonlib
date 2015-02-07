from dreambox.aws.core import aws_ec2cmd
from funcy.seqs import *
from itertools import chain


class ec2:
    profile=''
    region=''
    instances=None

    def __init__(self, profile='dreambox', region='us-east-1'):
       self.profile = profile
       self.region = region

    def describe_instances(self, **options):
        self.instances = aws_ec2cmd(self.profile,
                self.region,
                'describe-instances',
                **options)
