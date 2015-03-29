from dreambox.aws.core import aws_ec2cmd
from dreambox.aws.core import aws_asgcmd
from dreambox.aws.core import aws_cfn_cmd
from funcy.strings import str_join
from funcy.seqs import chunks
from funcy.seqs import pairwise
from itertools import chain
import os
import dreambox.utils
import re
from docopt import docopt
import pprint

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
def get_all_asgs(ec2profile='dreambox',
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
def get_all_play_asgs(ec2profile='dreambox',
                      ec2region='us-east-1',
                      env='production',
                      **options):
    qry='AutoScalingGroups[*].[Tags[?Key==`Name`].Value,Instances[].InstanceId][]'
    hashes = dreambox.utils.make_hash_of_hashes(get_all_asgs(ec2profile,
                                                             ec2region,
                                                             query=qry))
    result = {}
    regex_pattern = r"{0}-(:?play_*|product_admin)".format(env)
    print "compiling regex pattern: {0}".format(regex_pattern)
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
def get_only_play_asgs(ec2profile='dreambox',
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
def get_ec2_instances_hostnames_from_asg_groups(ec2profile='dreambox',
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

def get_available_stack_from_all_regions(profile=''):
    region_stacks = get_stack_names_from_all_regions(profile='mgmt')
    m = re.compile(r'\w+(\d)', re.IGNORECASE)
    def get_number(n):
        found = m.match(n)
        if found:
            return ord(found.group(1)) - 48

    region_available_slot = {}
    region_stack_slots = {}
    available_slot = None
    for region, stacks in region_stacks.items():
        region_stack_slots[region] = sorted(map(get_number, stacks))
        available_slot = __get_free_stack_from_a_slot(region_stack_slots[region])
        region_available_slot[region] = "Stage{0}".format(available_slot)
        break


    return region_available_slot

def __get_free_stack_from_a_slot(region=[]):
    available_slot = None

    pp = pprint.PrettyPrinter(indent=3)
    paired_list = pairwise(region)
    for pair in paired_list:
        pp.pprint(pair)
        if pair[1] - pair[0] > 1:
            available_slot = pair[0] + 1
            break
    return available_slot

def deploy(argv=[]):
    """
usage: deploy <command> [--all] [--inc-magic-number] [<args>...]

options:

commonly use operations:
ops deploy get-all-asgs [options]   # get all auto scaling groups define under AWS
    """
    print "pass in parameters: {0}".format(argv)
    print docopt(deploy.__doc__, options_first=True, argv=argv)


if __name__ == '__main__':
    import re
    import pprint

    pp = pprint.PrettyPrinter(indent=3)
    current_directory = os.path.dirname(os.path.realpath(__file__))
    print "script executed: %s and current script directory is: %s" % \
        (__file__, current_directory)
    asg_query='AutoScalingGroups[*].[Tags[?Key==`Name`].Value,Instances[].InstanceId][]'
    result = get_all_play_asgs(ec2profile='dreambox',
                           ec2region='us-east-1',
                           env='production',
                           query=asg_query)
    print 'result from get_all_play_asgs'
    print '============================'
    pp.pprint(result)
    print 'end of get_all_play_asgs'
    print '============================'
    print

    print 'result from get_only_play_asgs'
    print '=============================='
    result = get_only_play_asgs(query=asg_query)
    pp.pprint(result)
    print 'end of get_only_play_asgs'
    print

    asg_query='AutoScalingGroups[*].[Tags[?Key==`Name`].Value,Instances[].InstanceId][]'
    result = get_only_play_asgs(query=asg_query)

    print 'result from get_ec2_instances_hostnames_from_asg_groups'
    print '======================================================='
    results = get_ec2_instances_hostnames_from_asg_groups(asg_group=result)
    pp.pprint(results)
    print 'end of get_ec2_instances_hostnames_from_asg_groups'
    print '=================================================='
    print

    # print 'result from get_stack_names_from_all_regions'
    # print '==========================================='
    # results = get_stack_names_from_all_regions(profile = 'mgmt')
    # pp.pprint(results)
    # print 'end of get_stack_names_from_all_regions'
    # print '==========================================='
    # print

    print 'result from get_available_stack_from_all_regions'
    print '================================================'
    result = get_available_stack_from_all_regions(profile='mgmt')
    pp.pprint(result)
    print 'end of get_available_stack_from_all_regions'
    print '================================================'
