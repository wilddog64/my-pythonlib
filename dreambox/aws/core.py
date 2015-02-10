import json
from funcy.strings import str_join
import subprocess
import os
import re


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
# note: most aws sub-command options has a '-', which cash with python
#       keyword.  to solve this problem, when specify sub-command options,
#       use '_' instead of '-'.  this function will replace '_' with '-' for
#       all the instances it can find.
def aws_cmd(cmd_cat='',
            profile='dreambox',
            region='us-east-1',
            subcmd='',
            dry_run=False,
            **options):

    cmd_opts = ''
    my_options = {}
    if options:
        cmd_opts = ''
        for k, v in options.items():
            if '_' in k:
                k = re.sub('_', '-', k)
                print 'option key {}'.format(k)
                my_options[k] = v
            else:
                my_options[k] = v
        cmd_opts = ' '.join(["--{} {}".format(key, val)
                             for key, val in my_options.items()])
    aws_command = "aws --profile {} --region {} {} {} {}".format(profile,
             region, cmd_cat, subcmd, cmd_opts)
    if dry_run:
        aws_command = "{0} --dry-run".format(aws_command)
    print "prepare to execute %s " % aws_command
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
               ec2profile='dreambox',
               ec2region='us-east-1',
               subcmd='',
               **options):
    return aws_cmd('ec2',
            ec2profile,
            ec2region,
            subcmd,
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
def aws_asgcmd(aws_profile='dreambox',
               aws_region='us-east-1',
               asg_subcmd=None,
               **asg_options):
    return aws_cmd(cmd_cat='autoscaling',
            profile=aws_profile,
            region=aws_region,
            subcmd=asg_subcmd,
            **asg_options)


if __name__ == "__main__":
    from dreambox.ops.deployment import get_all_asgs
    from dreambox.ops.deployment import get_all_play_asgs
    from dreambox.ops.deployment import get_only_play_asgs
    from dreambox.ops.deployment import get_ec2_instances_hostnames_from_asg_groups
    import pprint

    pp = pprint.PrettyPrinter(indent=3)
    current_directory = os.path.dirname(os.path.realpath(__file__))
    print "script executed: %s and current script directory is: %s" % \
        (__file__, current_directory)
    # aws_ec2cmd('dreambox', 'us-east-1', 'describe-instances',
    #         query='Reservations[].Instances[].[PublicDnsName,KeyName]')
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

    print 'result from get_ec2_instances_hostnames_from_asg_groups'
    print '======================================================='
    results = get_ec2_instances_hostnames_from_asg_groups(asg_group=result)
    pp.pprint(results)
    print 'end of get_ec2_instances_hostnames_from_asg_groups'
    print '=================================================='
    print
