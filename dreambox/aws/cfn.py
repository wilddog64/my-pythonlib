from dreambox.aws.core import aws_cfn_cmd

class cfn:
    profile=''
    regions=[]
    stack_name=''
    query=''
    stacks={}

    def __init__(self, profile='', regions=['us-east-1', 'us-west-2']):
        self.profile = profile
        self.regions = regions

    def describe_stacks(self, **options):
        for region in self.regions:
            self.stacks[region] = []
            self.stacks[region] = aws_cfn_cmd(aws_profile=self.profile,
                                              aws_region=region,
                                              cfn_subcmd='describe-stacks',
                                              **options)

if __name__ == '__main__':
    from dreambox.aws.cfn import cfn
    import pprint

    pp = pprint.PrettyPrinter(indent=3)
    qry='Stacks[].StackName[]'
    cfn_obj = cfn()
    cfn_obj.describe_stacks(query=qry)
    pp.pprint(cfn_obj.stacks)
