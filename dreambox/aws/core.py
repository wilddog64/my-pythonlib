from __future__ import print_function
import json
from funcy.strings import str_join
import subprocess
import os
import re
import sys


# base function for all other aws command line function.  this function
# accepts 5 parameters,
#
#   cmd_cat: is a aws command category. this can be ec2, autoscaling ...
#   profile: a profile that aws command will reference
#   region: which region aws is going to tackle
#   subcmd: a sub command for aws command category
#   dry_run: checks whether you have the required permissions for the
#     action, without actually making the request. Using this option
#     will result in one of two possible error responses. If you have
#     the required permissions the error response will be DryRunOperation.
#     Otherwise it will be UnauthorizedOperation
#   **options: is a dict parameters that can pass to this particular
#              sub-command
#
# note: most aws sub-command options has a '-', which crash with python
#       keyword.  to solve this problem, when specify sub-command options,
#       use '_' instead of '-'.  this function will replace '_' with '-' for
#       all the instances it can find.
def aws_cmd(cmd_cat='',
            profile=None,
            region='us-east-1',
            subcmd='',
            dry_run=False,
            verbose=False,
            **options):

    cmd_opts = ''
    my_options = {}
    if options:
        cmd_opts = ''
        for k, v in options.items():
            if '_' in k:
                k = re.sub('_', '-', k)
                print('option key {}'.format(k), file=sys.stderr)
                my_options[k] = v
            else:
                my_options[k] = v
        cmd_opts = ' '.join(["--{} {}".format(key, val)
                             for key, val in my_options.items()])

    if profile:
        aws_command = "aws --profile {} --region {} {} {} {}".format(profile,
                 region, cmd_cat, subcmd, cmd_opts)
    else:
        aws_command = "aws --region {} {} {} {}".format(region,
                                                        cmd_cat,
                                                        subcmd,
                                                        cmd_opts)
    if dry_run:
        print('dry run flag set, executing {}'.format(aws_command),
              file=sys.stderr)
        return

    if verbose:
        print("prepare to execute %s " % aws_command, file=sys.stderr)
    cmd = aws_command.split(' ')
    proc = subprocess.Popen(cmd,
                            stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE
                            )
    result, error = proc.communicate()
    if not error:
        return json.loads(result)
    else:
        return error


# aws_ec2cmd is a function that will execute aws ec2 command category.  this
# function takes the following parameters,
#
#   ec2profile: profile defined in ~/.aws/config
#   ec2region: a region this function intend to work
#   subcmd: a sub-command that apply to aws ec2 command
#   **options: a list of command options that are applicable to a given
#     sub-command
#
# a json object will return upon a successful call
def aws_ec2cmd(
               ec2profile=None,
               ec2region='us-east-1',
               subcmd='',
               dry_run=False,
               verbose=False,
               **options):
    return aws_cmd('ec2',
                   ec2profile,
                   ec2region,
                   subcmd,
                   dry_run,
                   verbose,
                   **options)


# aws_asgcmd is a function that execute aws autoscaling command.  this
# function takes 5 parameters,
#
#  aws_profile: profile define under ~/.aws/config
#  aws_region: an aws region to work with
#  asg_sugcmd: a sub-command applicable to autoscaling
#  **asg_options: a list of acceptable options to autoscaling sub-command
#
# aws_asgcmd will return a valid json object back to caller upon successful
# call
def aws_asgcmd(aws_profile=None,
               aws_region='us-east-1',
               asg_subcmd=None,
               dry_run=False,
               verbose=False,
               **asg_options):
    return aws_cmd(cmd_cat='autoscaling',
                   profile=aws_profile,
                   region=aws_region,
                   subcmd=asg_subcmd,
                   dry_run=dry_run,
                   verbose=verbose,
                   **asg_options)

# aws_ecachecmd is a function that execute aws elasticache command.  this
# function takes 5 parameters,
#
#  aws_profile: profile define under ~/.aws/config
#  aws_region: an aws region to work with
#  asg_sugcmd: a sub-command applicable to autoscaling
#  **ecache_options: a list of acceptable options to elasticache sub-command
#
# aws_ecachecmd will return a valid json object back to caller upon successful
# call
def aws_ecachecmd(aws_profile=None,
                  aws_region='us-west-2',
                  ecache_subcmd=None,
                  dry_run=False,
                  verbose=False,
                  **ecache_options):
    return aws_cmd(
            cmd_cat='elasticache',
            profile=aws_profile,
            region=aws_region,
            subcmd=ecache_subcmd,
            dry_run=dry_run,
            verbose=verbose,
            **ecache_options)

def aws_cfn_cmd(aws_profile=None,
                aws_region='us-east-1',
                cfn_subcmd='',
                **cfn_options):
    return aws_cmd(cmd_cat='cloudformation',
                   profile=aws_profile,
                   region=aws_region,
                   subcmd=cfn_subcmd,
                   **cfn_options
                   )

# aws_rdscmd is a function that execute aws elasticache command.  this
# function takes 5 parameters,
#
#  aws_profile: profile define under ~/.aws/config
#  aws_region: an aws region to work with
#  asg_sugcmd: a sub-command applicable to autoscaling
#  **ecache_options: a list of acceptable options to elasticache sub-command
#
# aws_rdscmd will return a valid json object back to caller upon successful
# call
def aws_rdscmd(aws_profile=None,
                  aws_region='us-west-2',
                  rds_subcmd=None,
                  dry_run=False,
                  verbose=False,
                  **ecache_options):
    return aws_cmd(
            cmd_cat='rds',
            profile=aws_profile,
            region=aws_region,
            subcmd=rds_subcmd,
            dry_run=dry_run,
            verbose=verbose,
            **ecache_options)


# aws_redshiftcmd is a function that execute aws elasticache command.  this
# function takes 5 parameters,
#
#  aws_profile: profile define under ~/.aws/config
#  aws_region: an aws region to work with
#  asg_subcmd: a sub-command applicable to autoscaling
#  **ecache_options: a list of acceptable options to elasticache sub-command
#
# aws_redshiftcmd will return a valid json object back to caller upon successful
# call
def aws_redshiftcmd(aws_profile=None,
                    aws_region='us-west-2',
                    redshift_subcmd=None,
                    dry_run=False,
                    verbose=False,
                    **ecache_options):
    return aws_cmd(cmd_cat='redshift',
                   profile=aws_profile,
                   region=aws_region,
                   subcmd=redshift_subcmd,
                   dry_run=dry_run,
                   verbose=verbose,
                   **ecache_options)

if __name__ == "__main__":
    from dreambox.ops.deployment import get_all_play_asgs
    from dreambox.ops.deployment import get_only_play_asgs
    from dreambox.ops.deployment import get_ec2_instances_hostnames_from_asg_groups
    import pprint

    pp = pprint.PrettyPrinter(indent=3)
    current_directory = os.path.dirname(os.path.realpath(__file__))
    print("script executed: {0} and current script directory is: {1}".format(__file__, current_directory), file=sys.stderr)
    asg_query = 'AutoScalingGroups[*].[Tags[?Key==`Name`].Value,Instances[].InstanceId][]'
    result = get_all_play_asgs(ec2profile='dreambox',
                               ec2region='us-east-1',
                               env='production',
                               query=asg_query)
    print('result from get_all_play_asgs', file=sys.stderr)
    print('============================', file=sys.stderr)
    pp.pprint(result)
    print('end of get_all_play_asgs', file=sys.stderr)
    print('============================', file=sys.stderr)

    print('result from get_only_play_asgs', file=sys.stderr)
    print('==============================', file=sys.stderr)
    result = get_only_play_asgs(query=asg_query)
    pp.pprint(result)
    print('end of get_only_play_asgs', file=sys.stderr)
    print()

    print('result from get_ec2_instances_hostnames_from_asg_groups', file=sys.stderr)
    print('=======================================================', file=sys.stderr)
    results = get_ec2_instances_hostnames_from_asg_groups(asg_group=result)
    pp.pprint(results)
    print('end of get_ec2_instances_hostnames_from_asg_groups', file=sys.stderr)
    print('==================================================', file=sys.stderr)
    print()

    results = aws_cfn_cmd(aws_region='us-east-1',
                          cfn_subcmd='describe-stacks',
                          query='Stacks[].StackName[]')
    pp.pprint(results)
