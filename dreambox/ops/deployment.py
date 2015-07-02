from __future__ import print_function
from dreambox.aws.core import aws_ec2cmd
from dreambox.aws.core import aws_asgcmd
from dreambox.aws.core import aws_cfn_cmd
from dreambox.aws.core import aws_ecachecmd
from dreambox.aws.core import aws_rdscmd
from dreambox.aws.core import aws_redshiftcmd
from funcy.strings import str_join
from funcy.seqs import chunks
from funcy.seqs import pairwise
from itertools import chain
import os
import dreambox.utils
import re
from docopt import docopt
import pprint
import sys

__doc__ = """
usage: deployment [--profie] [--region] [--help] <command> [<args>...]

options:
    --profile  # aws profile
    --region   # region support by aws

commonly use operation
deployment get-all-asgs   # get all auto scaling groups define under AWS
"""
# get_all_asgs is a function that will return all the ASG defined for
# a given region for AWS.  The function takes the following parameters,
#
#   ec2profile: a n ec2 profile defined under ~/.aws/config
#   ec2region: a valid region defined by AWS service
#   env: which envirnoment we are talking about. set to production by default
#   **options: a list of options that applying to
#              autoscaling describe-auto-scaling-groups
#
# this function will return a list of hashes upon a successful call
def get_all_asgs(ec2profile=None,
                 ec2region='us-east-1',
                 **options):
    return aws_asgcmd(aws_profile=ec2profile,
                      aws_region=ec2region,
                      asg_subcmd='describe-auto-scaling-groups',
                      **options)

# get_play_asgs function will get all the play machine instances and store them
#   in a list of hashes.  this function takes the following parameters,
#
#   ec2profile: an ec2 profile stores in ~/.aws/config
#   ec2region: a region we are working on
#   env: environment we are looking for
#   **options: a list of options that can be accepted by
#     autoscaling describe-auto-scaling-groups
def get_all_play_asgs(ec2profile=None,
                      ec2region='us-east-1',
                      env='production',
                      **options):
    qry='AutoScalingGroups[*].[Tags[?Key==`Name`].Value,Instances[].InstanceId][]'
    hashes = dreambox.utils.make_hash_of_hashes(get_all_asgs(ec2profile,
                                                             ec2region,
                                                             query=qry))
    result = {}
    regex_pattern = r"{0}-(:?play_*|product_admin)".format(env)
    print("compiling regex pattern: {0}".format(regex_pattern), file=sys.stderr)
    re_match = re.compile(regex_pattern, re.I)
    for k, v in hashes.items():
        if re_match.match(k) and '-db-' not in k:
            result[k.lower()] = v

    return result


# get_only_play_asgs will return all the play asg except _corn_ or _admin with
# the group names. this function accepts the following parameters,
#
#  ec2profile: a profile that is defined under ~/.aws/config
#  ec2region: region in AWS this function works on
#  env: what environment we are looking for
#  **options: a list of command line options that are applicable to
#     autoscaling describe-auto-scaling-groups
def get_only_play_asgs(ec2profile=None,
                       ec2region='us-east-1',
                       env='production',
                       **options):
    all_play_asgs = get_all_play_asgs(ec2profile, ec2region, env, **options)
    result = {}
    for k, v in all_play_asgs.items():
        if '_cron_' not in k.lower() and '_admin' not in k.lower():
            result[k] = v
    return result

# get_ec2_instances_hostnames_from_asg_groups will get instance hostnames from
# a given ASG group.  This function takes the following parameters,
#
#   ec2profile is profile defines in ~/.aws/config
#   ec2region
def get_ec2_instances_hostnames_from_asg_groups(ec2profile=None,
                                                ec2region='us-east-1',
                                                asg_group={}):
    qry='Reservations[].[Instances[].[PublicDnsName,Tags[?Key==`Name`]]][][][]'
    results = []
    for k, v in asg_group.items():
        if v:
            ids = str_join(' ', v)
            result = aws_ec2cmd(ec2profile,
                                ec2region,
                                subcmd='describe-instances',
                                instance_ids=ids,
                                query=qry)
            results.append(result)
    return chunks(2, list(chain.from_iterable(results)))

# get_stack_names_from_all_regions will return all stacks from known
# AWS regions (by default these regions are us-east-1 and us-west-2).  The
# function accepts 3 parameters,
#
#   profile: a profile define in ~/.aws/config
#   regions: a list of AWS region that this function will retrieve stack names
#   qry: a json query string
#
# get_stack_names_from_all_regions will only return name with stageN (n is a
# number from 1 - 9)
def get_stack_names_from_all_regions(profile = '',
                                     regions = [ 'us-east-1', 'us-west-2' ],
                                     qry = 'Stacks[].StackName'):
    region_stacks = {}
    m = re.compile(r'^stage\d$', re.IGNORECASE)
    for region in regions:
        region_stack = [r for r in
                          aws_cfn_cmd(aws_profile = profile,
                                      aws_region = region,
                                      cfn_subcmd = 'describe-stacks',
                                      query = qry)
                          if m.match(r)
                        ]
        region_stacks[region] = region_stack

    return region_stacks

# get_available_stack_from_all_regions will return first available stack
# environment from all regions.  The function takes these parameters,
#
#   aws_profile is a profile defined in ~/.aws/config
#
# This function will search a given set of regions and return the first
# available stack and return it as a hash of array back to caller
def get_available_stack_from_all_regions(aws_profile=''):

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

def get_all_ec2_security_groups(ec2profile=None,
                                regions=['us-east-1', 'us-west-2'],
                                filterby=None):

    results        = []
    for region in regions:
        result = aws_ec2cmd(ec2profile,
                            region,
                            subcmd='describe-security-groups',
                            query='SecurityGroups[].GroupName')
        results.extend(result)

    return __filter_list_by(result, myfilter=filterby)


def get_all_elasticcache_security_groups(ec2profile=None,
                                         regions=['us-east-1', 'us-west-2'],
                                         filterby=None):

    results        = []
    for region in regions:
        result = aws_ecachecmd(
         ec2profile,
         region,
         ecache_subcmd='describe-cache-security-groups',
         query='CacheSecurityGroups[].EC2SecurityGroups[].EC2SecurityGroupName')
        results.extend(result)

    return __filter_list_by(result, myfilter=filterby)


def get_all_rds_security_groups(ec2profile=None,
                                regions=['us-east-1', 'us-west-2'],
                                filterby=None):

    results        = []
    for region in regions:
        result = aws_rdscmd(
         ec2profile,
         region,
         rds_subcmd='describe-db-security-groups',
         query='DBSecurityGroups[].EC2SecurityGroups[].EC2SecurityGroupName')
        results.extend(result)

    return __filter_list_by(result, myfilter=filterby)


def get_all_redshift_security_groups(ec2profile=None,
                                regions=['us-east-1', 'us-west-2'],
                                filterby=None):

    results        = []
    for region in regions:
        result = aws_redshiftcmd(
         ec2profile,
         region,
         redshift_subcmd='describe-cluster-security-groups',
         query='ClusterSecurityGroups[].EC2SecurityGroups[].EC2SecurityGroupName')
        results.extend(result)

    return __filter_list_by(result, myfilter=filterby)


def get_all_security_groups(my_ec2profile=None,
                            my_regions=['us-east-1', 'us-west-2'],
                            my_filterby=None):
    results = {}
    results['ec2'] = get_all_ec2_security_groups(ec2profile=my_ec2profile,
                                                 regions=my_regions,
                                                 filterby=my_filterby)
    results['elasticcache'] = get_all_elasticcache_security_groups(
                                      ec2profile=my_ec2profile,
                                      regions=my_regions,
                                      filterby=my_filterby)
    results['rds'] = get_all_rds_security_groups(ec2profile=my_ec2profile,
                                                 regions=my_regions,
                                                 filterby=my_filterby)
    results['redshift'] = get_all_redshift_security_groups(
                                      ec2profile=my_ec2profile,
                                      regions=my_regions,
                                      filterby=my_filterby)
    return results

def __filter_list_by(my_list=[], myfilter=None):
    result = []
    if not myfilter is None:
        result = [p for p in my_list
            if p.capitalize().startswith(myfilter.capitalize())]
    else:
        result = my_list
    return result

def execute(argv=[]):
    """
usage: deploy [--all] [--inc-magic-number] [<args>...]

options:

commonly use operations:
ops deploy [options]   # get all auto scaling groups define under AWS

    """
    print("pass in parameters: {0}".format(argv), file=sys.stderr)
    arguments = docopt(execute.__doc__, argv=argv)
    print("argument receive: {}".format(arguments), file=sys.stderr)

if __name__ == '__main__':
    import re
    import pprint

    pp = pprint.PrettyPrinter(indent=3)
    current_directory = os.path.dirname(os.path.realpath(__file__))
    print("script executed: %s and current script directory is: %s" % \
        (__file__, current_directory), file=sys.stderr)
    asg_query='AutoScalingGroups[*].[Tags[?Key==`Name`].Value,Instances[].InstanceId][]'
    result = get_all_play_asgs(ec2profile=None,
                           ec2region='us-east-1',
                           env='production',
                           query=asg_query)
    print('result from get_all_play_asgs', file=sys.stderr)
    print('============================', file=sys.stderr)
    pp.pprint(result)
    print('end of get_all_play_asgs', file=sys.stderr)
    print('============================', file=sys.stderr)
    print("\n", file=sys.stderr)

    print('result from get_only_play_asgs', file=sys.stderr)
    print('==============================', file=sys.stderr)
    result = get_only_play_asgs(query=asg_query)
    pp.pprint(result)
    print('end of get_only_play_asgs', file=sys.stderr)
    print("\", file=sys.stderr")

    asg_query='AutoScalingGroups[*].[Tags[?Key==`Name`].Value,Instances[].InstanceId][]'
    result = get_only_play_asgs(query=asg_query)

    print('result from get_ec2_instances_hostnames_from_asg_groups', file=sys.stderr)
    print('=======================================================', file=sys.stderr)
    results = get_ec2_instances_hostnames_from_asg_groups(asg_group=result)
    pp.pprint(results)
    print('end of get_ec2_instances_hostnames_from_asg_groups', file=sys.stderr)
    print('==================================================', file=sys.stderr)
    print("\n", file=sys.stderr)

    print('result from get_available_stack_from_all_regions', file=sys.stderr)
    print('================================================', file=sys.stderr)
    result = get_available_stack_from_all_regions()
    pp.pprint(result)
    print('end of get_available_stack_from_all_regions', file=sys.stderr)
    print('===========================================', file=sys.stderr)

    print( 'result from get_all_ec2_security_groups' )
    print('================================================', file=sys.stderr)
    result = get_all_ec2_security_groups()
    pp.pprint(result)

    print('filter by stage2')
    print('================================================', file=sys.stderr)
    filter_result = get_all_ec2_security_groups(filterby='Stage2')
    pp.pprint(filter_result)
    print( 'end of get_all_ec2_security_groups' )
    print('================================================', file=sys.stderr)

    print( 'result from get_all_elasticcache_security_groups' )
    print('================================================', file=sys.stderr)
    result = get_all_elasticcache_security_groups()
    pp.pprint(result)
    print( 'filter by stage2' )
    result = get_all_elasticcache_security_groups(filterby='stage3')
    pp.pprint(result)
    print( 'end of get_all_elasticcache_security_groups' )
    print('================================================', file=sys.stderr)

    print( 'result from get_all_rds_security_groups' )
    print('================================================', file=sys.stderr)
    result = get_all_rds_security_groups()
    pp.pprint(result)
    print( 'filter by stage2' )
    result = get_all_rds_security_groups(filterby='stage3')
    pp.pprint(result)
    print( 'end of get_all_rds_security_groups' )
    print('================================================', file=sys.stderr)

    print( 'result from get_all_redshift_security_groups' )
    print('================================================', file=sys.stderr)
    result = get_all_redshift_security_groups()
    pp.pprint(result)
    print( 'filter by stage3' )
    result = get_all_redshift_security_groups(filterby='stage3')
    pp.pprint(result)
    print( 'end of get_all_redshift_security_groups' )
    print('================================================', file=sys.stderr)

    print( 'result from get_all_security_groups' )
    print('================================================', file=sys.stderr)
    result = get_all_security_groups()
    pp.pprint(result)
    print( 'result from get_all_security_groups filtered by stage2' )
    result = get_all_security_groups(my_filterby='stage2')
    pp.pprint(result)
    print( 'end of get_all_security_groups' )
    print('================================================', file=sys.stderr)
