from __future__ import print_function
from dreambox.aws.core import aws_ec2cmd
from dreambox.aws.core import aws_asgcmd
from dreambox.aws.core import aws_cfn_cmd
from funcy.strings import str_join
from funcy.seqs import chunks
from funcy.seqs import pairwise
from funcy.colls import select
from itertools import chain
import dreambox.aws.security
import dreambox.utils
import re
import sys

def get_all_asgs(ec2profile=None,
                 ec2region='us-east-1',
                 **options):
    '''
get_all_asgs is a function that will return all the ASG defined for
a given region for AWS.  The function takes the following parameters,

  ec2profile: a n ec2 profile defined under ~/.aws/config
  ec2region: a valid region defined by AWS service
  env: which envirnoment we are talking about. set to production by default
  **options: a list of options that applying to
             autoscaling describe-auto-scaling-groups

this function will return a list of hashes upon a successful call
    '''
    return aws_asgcmd(aws_profile=ec2profile,
                      aws_region=ec2region,
                      asg_subcmd='describe-auto-scaling-groups',
                      **options)

def get_all_play_asgs(ec2profile=None,
                      ec2region='us-east-1',
                      env='production',
                      **options):
    '''
get_play_asgs function will get all the play machine instances and store them
  in a list of hashes.  this function takes the following parameters,

  ec2profile: an ec2 profile stores in ~/.aws/config
  ec2region: a region we are working on
  env: environment we are looking for
  **options: a list of options that can be accepted by
    autoscaling describe-auto-scaling-groups
    '''
    qry = 'AutoScalingGroups[*].[Tags[?Key==`Name`].Value,Instances[].InstanceId][]'
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


def get_only_play_asgs(ec2profile=None,
                       ec2region='us-east-1',
                       env='production',
                       **options):
    '''
get_only_play_asgs will return all the play asg except _corn_ or _admin with
the group names. this function accepts the following parameters,

 ec2profile: a profile that is defined under ~/.aws/config
 ec2region: region in AWS this function works on
 env: what environment we are looking for
 **options: a list of command line options that are applicable to
    autoscaling describe-auto-scaling-groups
    '''
    all_play_asgs = get_all_play_asgs(ec2profile, ec2region, env, **options)
    result = {}
    for k, v in all_play_asgs.items():
        if '_cron_' not in k.lower() and '_admin' not in k.lower():
            result[k] = v
    return result

def get_ec2_instances_hostnames_from_asg_groups(ec2profile=None,
                                                ec2region='us-east-1',
                                                asg_group={}):
    '''
get_ec2_instances_hostnames_from_asg_groups will get instance hostnames from
a given ASG group.  This function takes the following parameters,

  ec2profile is profile defines in ~/.aws/config
  ec2region
    '''
    qry='Reservations[].[Instances[].[PublicDnsName,Tags[?Key==`Name`]]][][][]'
    results = []
    for k, v in asg_group.items():
        if v:
            ids = str_join(' ', v)
            result, error = aws_ec2cmd(ec2profile,
                                       ec2region,
                                       subcmd='describe-instances',
                                       instance_ids=ids,
                                       query=qry)
            if error:
                sys.exit(error)
            results.append(result)
    return chunks(2, list(chain.from_iterable(results)))

def get_all_autoscaling_group_from(profile=None,
                                   region=None,
                                   filterby=None):
    '''
get_all_autoscaling_group_from will return all the autoscaling groups for a
given stage environment
    '''
    asg_result, error = aws_asgcmd(aws_profile=profile,
                                   aws_region=region,
                                   asg_subcmd='describe-auto-scaling-groups',
                                   query='AutoScalingGroups[].AutoScalingGroupName')

    if error:
        sys.exit(error)

    return_result = None
    if filterby is None:
        return_result = asg_result
    else:
        return_result = select(lambda x: filterby.lower() in x.lower(), asg_result)
    return return_result


def suspend_autoscaling_groups_for_stage(profile=None,
                                         region=None,
                                         filterby=None,
                                         verbose=False,
                                         dry_run=False):
    '''
suspend_autoscaling_groups_for_stage will suspend autoscaling groups bsaed on
a filterby parameter.  This function returns nothing.
    '''
    asg_groups = get_all_autoscaling_group_from(profile=profile,
                                                region=region,
                                                filterby=filterby)
    for asg_group in asg_groups:
        aws_asgcmd(aws_profile=profile,
                   aws_region=region,
                   asg_subcmd='suspend-processes',
                   auto_scaling_group_name=asg_group,
                   verbose=verbose,
                   dry_run=dry_run)


if __name__ == '__main__':

    print('testing get_all_autoscaling_group_from with stage3 environment',
          file=sys.stderr)
    result = get_all_autoscaling_group_from(region='us-west-2',
                                                 filterby='stage3')
    dreambox.utils.print_structure(result)
    print('end testing get_all_autoscaling_group_from with filter')
    print()
    print('testing get_all_autoscaling_group_from without any filter')
    result = get_all_autoscaling_group_from(region='us-west-2')
    dreambox.utils.print_structure(result)
    print('end testing get_all_autoscaling_group_from without filter')
    print()
    print('testing suspend_autoscaling_groups_for_stage filter by stage3')
    suspend_autoscaling_groups_for_stage(region='us-west-2',
                                         filterby='stage3',
                                         dry_run=True,
                                         verbose=True)
    print('end testing suspend_autoscaling_groups_for_stage filter by stage3')
