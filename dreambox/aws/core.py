from __future__ import print_function
import json
import subprocess
import re
import sys
import dreambox.utils
import sh
from sh import aws

def __aws(cmd=None, subcmd=None, **kwargs):
    aws_func = None
    output = None
    if hasattr(aws, cmd):
        aws_func = getattr(aws, cmd)
    else:
      raise Exception('cmd %s is not support by awscli' % cmd)
    
    output = aws_func(subcmd, **kwargs)
    json_obj = None
    if output and output.stdout:
       json_obj = json.loads(output.stdout) 

    return json_obj


def ec2(*args, **kwargs):
    """
ec2 is a aws command that perform a command aws ec2 operations
    """
    ec2_json_obj = __aws('ec2', *args, **kwargs)
    return ec2_json_obj


def autoscaling(*args, **kwargs):
    '''
autoscaling is an AWS command that perform autoscaling related
operations
    '''
    autoscaling_json_obj = __aws('autoscaling', *args, **kwargs)

    return autoscaling_json_obj


def elasticache(*args, **kwargs):
    '''
elasticache is a function that performs aws elasticache function
    '''
    elasticache_json_obj = __aws('elasticache', *args, **kwargs)
    return elasticache_json_obj


def rds(*args, **kwargs):
    '''
rds is a function that perform aws rds operations
    '''
    rds_json_obj = __aws('rds', *args, **kwargs)

    return rds_json_obj

def cloudformation(*args, **kwargs):
    '''
cloudformation is a function that performs aws cloudformation
operations
    '''
    cfn_json_obj = __aws('cloudformation', *args, **kwargs)

    return cfn_json_obj

def redshift(*args, **kwargs):
    '''
 redshift is a function that performs a command aws redshift coperations 
    '''
    redshift_json_obj = __aws('redshift', *args, **kwargs)

    return redshift_json_obj


def s3api(*args, **kwargs):
    '''
 s3api is a function that performs aws a3api operations 
    '''
    s3api_json_obj = __aws('s3api', *args, **kwargs)

    return s3api_json_obj


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
    if len(error) == 0:
        if len(result) > 0:
            return json.loads(result)


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
                dry_run=False,
                cfn_subcmd='',
                **cfn_options):
    return aws_cmd(cmd_cat='cloudformation',
                   profile=aws_profile,
                   region=aws_region,
                   dry_run=dry_run,
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


def aws_s3api_cmd(aws_profile=None,
                  aws_region='us-west-2',
                  s3api_subcmd=None,
                  dry_run=False,
                  verbose=False,
                  **s3api_options):

    '''
aws_s3api_cmd is based command to issure verious aws s3api command.  The function
takes the following parameters,


#  aws_profile: profile define under ~/.aws/config
#  aws_region: an aws region to work with
#  s3api_subcmd: a sub-command applicable to autoscaling
#  **s3api_options: a list of acceptable options to s3api sub-command
#
    '''
    if aws_region is None:
        aws_region = 'us-west-2'

    return aws_cmd(cmd_cat='s3api',
                   profile=aws_profile,
                   region=aws_region,
                   subcmd=s3api_subcmd,
                   dry_run=dry_run,
                   verbose=verbose,
                   **s3api_options)


if __name__ == "__main__":
    print()
    print('=== testing ec2 ===')
    output_instances = ec2('describe-instances',
                            region='us-west-2',
                            query='Reservations[].Instances[].[InstanceId,Tags[?Key==`Name`].Value]')
    dreambox.utils.print_structure(output_instances)
    print('=== end testing ec2 ===')
    print()
    print('==== testing autoscaling ===')
    autoscaling_groups = autoscaling('describe-auto-scaling-groups',
                                     region='us-west-2',
                                     query='AutoScalingGroups[].[AutoScalingGroupName,Tags[?Key==`Name`].Value]')
    dreambox.utils.print_structure(autoscaling_groups)
    print('==== end testing autoscaling ===')
    print()
    print('==== testing elasticache ===')
    elasticache_cluster = elasticache('describe-cache-clusters',
                                     region='us-west-2',)
    dreambox.utils.print_structure(elasticache_cluster)
    print('==== end testing elasticache ===')
    print()
    print('==== testing rds ===')
    rds_query='DBSecurityGroups[].[DBSecurityGroupName,EC2SecurityGroups[].[EC2SecurityGroupName,EC2SecurityGroupOwnerId]]'
    db_security_groups = rds('describe-db-security-groups',
                             region='us-west-2',
                             query=rds_query)
    dreambox.utils.print_structure(db_security_groups)
    print('==== end testing rds ===')
    print()
    print('==== testing cloudformation ====')
    stacks = cloudformation('describe-stacks',
                            region='us-west-2',
                            query='Stacks[].StackName',
                            )
    dreambox.utils.print_structure(stacks)
    print('==== end testing cloudformation ====')
    print()
    print('==== testing redshift ====')
    redshift('describe-cluster-security-groups',
             region='us-west-2')
    print('==== end testing redshift ====')
    print()
    print('==== testing s3api ===')
    s3buckets = s3api('list-buckets')
    dreambox.utils.print_structure(s3buckets)
    print('==== end testing s3api ===')
