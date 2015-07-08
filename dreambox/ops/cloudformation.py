from __future__ import print_function
from dreambox.aws.core import aws_cfn_cmd


# get_stack_names_from_all_regions will return all stacks from known
#
# AWS regions (by default these regions are us-east-1 and us-west-2).  The
# function accepts 3 parameters,
#
#   profile: a profile define in ~/.aws/config
#   regions: a list of AWS region that this function will retrieve stack names
#   qry: a json query string
#
# get_stack_names_from_all_regions will only return name with stageN (n is a
# number from 1 - 9)
def get_stack_names_from_all_regions(profile='',
                                     regions=None,
                                     qry='Stacks[].StackName'):

    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    region_stacks = {}
    m = re.compile(r'^stage\d$', re.IGNORECASE)
    for region in regions:
        region_stack = [r for r in
                          aws_cfn_cmd(aws_profile=profile,
                                      aws_region=region,
                                      cfn_subcmd='describe-stacks',
                                      query=qry)
                          if m.match(r)
                        ]
        region_stacks[region] = region_stack

    return region_stacks


