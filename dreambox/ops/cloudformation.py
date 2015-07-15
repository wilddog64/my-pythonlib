from __future__ import print_function
from dreambox.aws.core import aws_cfn_cmd
from funcy.colls import select
import dreambox.utils
import re
import sys


def get_stack_names_from_all_regions(profile='',
                                     regions=None,
                                     qry='Stacks[].StackName'):
    '''
get_stack_names_from_all_regions will return all stacks from known

AWS regions (by default these regions are us-east-1 and us-west-2).  The
function accepts 3 parameters,

  profile: a profile define in ~/.aws/config
  regions: a list of AWS region that this function will retrieve stack names
  qry: a json query string

get_stack_names_from_all_regions will only return name with stageN (n is a
number from 1 - 9)
    '''
    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    region_stacks = {}
    m = re.compile(r'^stage\d$', re.IGNORECASE)
    for region in regions:
        region_stack = [r for r in aws_cfn_cmd(aws_profile=profile,
                                               aws_region=region,
                                               cfn_subcmd='describe-stacks',
                                               query=qry)
                        if m.match(r)]
        region_stacks[region] = region_stack

    return region_stacks


def get_all_stacks_for_stage(profile=None,
                             region=None,
                             filterby=None):
    '''
get_all_stacks_for_stage will return all the stacks exists for a given stage
environment.  It takes the following parameters,

profile - aws profile if one exist.  If it is not provided, the function will
          try to use IAM profile if a given instance has one.
region - which aws region do we want to work on
filterby - limit result by providing a filter string
    '''
    stage_stacks = aws_cfn_cmd(aws_profile=profile,
                               aws_region=region,
                               cfn_subcmd='describe-stacks',
                               query='Stacks[].StackName')

    stacks_list = select(lambda x: filterby.lower() in x.lower(), stage_stacks)
    return stacks_list

if __name__ == '__main__':
    stacks = get_all_stacks_for_stage(region='us-west-2', filterby='stage3')
    dreambox.utils.print_structure(stacks)
