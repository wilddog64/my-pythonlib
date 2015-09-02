from __future__ import print_function
from dreambox.aws.core import aws_ec2cmd
from dreambox.aws.core import aws_asgcmd
from dreambox.aws.core import aws_cfn_cmd
from funcy.strings import str_join
from funcy.seqs import chunks
from funcy.seqs import pairwise
from itertools import chain
import dreambox.aws.security
import dreambox.aws.cloudformation
import os
import dreambox.utils
import re
from docopt import docopt
import sys

import dreambox.aws.autoscaling
import dreambox.aws.ec2 as ec2

def get_available_stack_from_all_regions(aws_profile=''):
    '''
get_available_stack_from_all_regions will return first available stack
environment from all regions.  The function takes these parameters,

  aws_profile is a profile defined in ~/.aws/config

This function will search a given set of regions and return the first
available stack and return it as a hash of array back to caller
    '''

    from dreambox.aws.cloudformation import get_stack_names_from_all_regions
    # get all the stacks from every region. at this point, we don't want
    # anything but the number attaches to the stack name
    region_stacks = get_stack_names_from_all_regions(profile=aws_profile)
    m = re.compile(r'\w+(\d)', re.IGNORECASE)
    def get_number(n):  # this is a callback function we filter out number
        found = m.match(n)
        if found:
            return ord(found.group(1)) - 48

    def get_free_stack_from_a_slot(region=[]):
        available_slot = None

        paired_list = pairwise(region)
        for pair in paired_list:
            if pair[1] - pair[0] > 1:
                available_slot = pair[0] + 1
                break
        return available_slot

    # go through the hash and collect the right pattern we want. we also sort
    # the list and calculate the first avaiable stack environment by calling
    # get_free_stack_from_a_slot private function.  The result is stored at
    # region_available_slot hash
    region_available_slot = {}
    region_stack_slots = {}
    available_slot = None
    my_region, my_slot = None, None
    for region, stacks in region_stacks.items():
        region_stack_slots[region] = sorted(map(get_number, stacks))
        available_slot = get_free_stack_from_a_slot(region_stack_slots[region])
        region_available_slot[region] = "Stage{0}".format(available_slot)
        my_region, my_slot = region, region_available_slot[region].lower()
        break

    build_properties_path = ''
    workspace = os.getcwd()
    if os.environ.has_key('WORKSPACE'):
        workspace = os.environ.get('WORKSPACE')
    build_properties_path = os.path.join(workspace, 'build.properties')

    with open(build_properties_path, 'w') as fh:
        fh.write("region={0}\nchef_environment={1}".format(my_region, my_slot))
    fh.closed

    # return result back to caller
    sys.stdout.write("region slot -> {0}:{1}".format(my_region, my_slot))
    return region_available_slot

def delete_all_security_groups(argv=None):
    """
usage:
    ops delete_all_security_groups <stage>...
    ops delete_all_security_groups <stage> [--dry-run=<no|yes>]

options:
ops delete_all_security_groups [options] # delete all security group for a given
environment
    """
    # print('pass in parameters: {}'.format(argv), file=sys.stderr)
    from dreambox.aws.security import delete_security_groups
    arguments = docopt(delete_all_security_groups.__doc__, argv=argv)
    stage = arguments['<stage>'][0]
    dry_run = arguments['--dry-run']
    print('stage to work on is {}'.format(stage), file=sys.stderr)
    print('--dry-run: {}'.format(dry_run), file=sys.stdout)
    delete_security_groups(my_filterby=stage, dry_run=dry_run)


def revoke_all_ingress_rules_for_stage(args=None):
    from dreambox.aws.security import revoke_all_ingress_rules
    revoke_all_ingress_rules(filterby=args.stage, dry_run=args.dry_run)


def get_all_ec2_instances_from_tag(argv=None):
    '''
usage:
    ops get_all_ec2_instances_from_tag <partial_tag>
    '''

    from dreambox.aws.ec2 import get_ec2_hosts_for_stage
    arguments = docopt(get_all_ec2_instances_from_tag.__doc__, argv=argv)
    partial_tag = arguments['<partial_tag>']
    if partial_tag.lower() == 'all':
      partial_tag=None

    print('query stage environment: {}'.format(partial_tag))
    stage_ec2_instances = get_ec2_hosts_for_stage(stage=partial_tag)
    dreambox.utils.print_structure(stage_ec2_instances)

def get_all_instances_for(args=None):
    profile=args.profile
    region=args.region
    filter_expression = args.expression

    def filterby(x):
        if x[0] is not None:
          return filter_expression in x[0][0]

    instance_query='Reservations[].Instances[].[Tags[?Key==`Name`].Value,PrivateIpAddress,PrivateDnsName,InstanceId]'
    instances = ec2.describe_instances(profile=profile,
                                       region=region,
                                       filterby=filterby,
                                       query=instance_query)
    dreambox.utils.print_structure(instances)

if __name__ == '__main__':

    current_directory = os.path.dirname(os.path.realpath(__file__))
    print("script executed: %s and current script directory is: %s" % \
        (__file__, current_directory), file=sys.stderr)
    asg_query = 'AutoScalingGroups[*].[Tags[?Key==`Name`].Value,Instances[].InstanceId][]'
    my_result = dreambox.aws.autoscaling.get_all_play_asgs(ec2profile=None,
                                                           ec2region='us-east-1',
                                                           env='production',
                                                           query=asg_query)
    print('result from get_all_play_asgs', file=sys.stderr)
    print('============================', file=sys.stderr)
    dreambox.utils.print_structure(my_result)
    print('end of get_all_play_asgs', file=sys.stderr)
    print('============================', file=sys.stderr)
    print("\n", file=sys.stderr)

    print('result from get_only_play_asgs', file=sys.stderr)
    print('==============================', file=sys.stderr)
    my_result = dreambox.aws.autoscaling.get_only_play_asgs(query=asg_query)
    dreambox.utils.print_structure(my_result)
    print('end of get_only_play_asgs', file=sys.stderr)
    print("\", file=sys.stderr")

    asg_query = 'AutoScalingGroups[*].[Tags[?Key==`Name`].Value,Instances[].InstanceId][]'
    my_result = dreambox.aws.autoscaling.get_only_play_asgs(query=asg_query)

    print('result from get_ec2_instances_hostnames_from_asg_groups', file=sys.stderr)
    print('=======================================================', file=sys.stderr)
    results = dreambox.aws.autoscaling.get_ec2_instances_hostnames_from_asg_groups(asg_group=my_result)
    dreambox.utils.print_structure(results)
    print('end of get_ec2_instances_hostnames_from_asg_groups', file=sys.stderr)
    print('==================================================', file=sys.stderr)
    print("\n", file=sys.stderr)

    print('result from get_available_stack_from_all_regions', file=sys.stderr)
    print('================================================', file=sys.stderr)
    my_result = get_available_stack_from_all_regions()
    dreambox.utils.print_structure(my_result)
    print('end of get_available_stack_from_all_regions', file=sys.stderr)
    print('===========================================', file=sys.stderr)

