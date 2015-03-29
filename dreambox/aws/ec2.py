from dreambox.aws.core import aws_ec2cmd
from funcy.seqs import *
from itertools import chain


class ec2:
    profile=''
    region=''
    instances=None
    dry_run=False

    def __init__(self, profile='dreambox', region='us-east-1', dry_run=False):
       self.profile = profile
       self.region = region
       self.dry_run = dry_run

    def describe_instances(self, **options):
        self.instances = aws_ec2cmd(self.profile,
                self.region,
                'describe-instances',
                **options)


if __name__ == '__main__':
    from dreambox.aws.ec2 import ec2
    import pprint

    pp = pprint.PrettyPrinter(indent=3)
    qry='Reservations[].[Instances[].[PublicDnsName,Tags[?Key==`Name`]]][][][]'
    ec2_obj = ec2()
    ec2_obj.describe_instances(query=qry)
    pp.pprint(ec2_obj.instances)
