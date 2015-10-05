from __future__ import print_function
import json
import subprocess
import re
import sys
import dreambox.utils
import sh
from sh import aws

# a custom error message to handle when aws cli command not taking
# --dry-run option
class DryRunError(sh.ErrorReturnCode):
    def __init__(self, message):
        super(sh.ErrorReturnCode, self).__init__(message)

def __aws(cmd=None, subcmd=None, **kwargs):
    '''
__aws is a base function to support all awscli commands, and 
sub-commands.  The function takes the following parameters,

* cmd is any valid awscli command
* subcmd is any valid awscli command sub-command
* **kwargs is a valid parameters belongs to any give sub-command

Most of the awscli will return a json text back when execute
successfully.  This function will check if any json text exists
in standard output, and return them as python object if text is
available.
    '''
    aws_func = None
    output = None

    # check if a given cmd is support by aws; raise an excpetion
    # if not
    if hasattr(aws, cmd):
        aws_func = getattr(aws, cmd)
    else:
      raise Exception('cmd %s is not support by awscli' % cmd)
  
    # if verbose is set, print out what is command line constructed.
    # verbose is not a valid awscli command options, so we have to 
    # delete it before we pass into awscli ccommand
    verbose = False
    if 'verbose' in kwargs and kwargs['verbose']:
       verbose = kwargs['verbose']
       del kwargs['verbose']
    elif 'verbose' in kwargs and not kwargs['verbose']:
       del kwargs['verbose']

    # if dry_run flag is set to False, then remove it from the **kwargs
    if 'dry_run' in kwargs and not kwargs['dry_run']:
        del kwargs['dry_run']

    func = aws_func.bake(subcmd, **kwargs)
    full_function_args =  func._path + ' ' + ' '.join(func._partial_baked_args)
    if verbose:
       dreambox.utils.print_structure(kwargs)
       print('executing %s' % full_function_args)

    # execute awscli command, and check if there's any output available
    # some awscli command will not accept --dry-run flag, so we raise our
    # custom exception to allow caller to capture and handle it.
    try:
        output = func()
    except sh.ErrorReturnCode_255 as err:
        if '--dry-run' in err.stderr:
            raise DryRunError(full_function_args)
    except sh.ErrorReturnCode:
        raise sh.ErrorReturnCode

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
    autoscaling_json_obj = None
    try:
        autoscaling_json_obj = __aws('autoscaling', *args, **kwargs)
    except DryRunError as dre:
        print('--dry-run flag set, executing %s' % dre.args[0])

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
    rds_json_obj = None
    try:
        rds_json_obj = __aws('rds', *args, **kwargs)
    except DryRunError as dre:
        print('--dry-run flag set, executing %s' % dre.args[0])

    return rds_json_obj

def cloudformation(*args, **kwargs):
    '''
cloudformation is a function that performs aws cloudformation
operations
    '''
    cfn_json_obj = None
    try:
        cfn_json_obj = __aws('cloudformation', *args, **kwargs)
    except DryRunError as dre:
        print('--dry-run flag set, executing %s' % dre.args[0])

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
    s3api_json_obj = None
    try:
        s3api_json_obj = __aws('s3api', *args, **kwargs)
    except DryRunError as dre:
        print('--dry-run flag set, executing %s' % dre.args[0])

    return s3api_json_obj

def json_to_pyobj(json_obj):
    '''
json_to_pyobj is a function that converts json object to
a python object.  This function takes one parameters,

* json_obj is a valid python hash that represents json

when the function executes successfully, a live python object
returns.
    '''
    def hash2obj(hash):
        if isinstance(hash, dict):
            return type('jo', (), {
                k: hash2obj(v) for k, v in hash.iteritems()
                })
        else:
            return hash

    return hash2obj(json_obj)

if __name__ == "__main__":
    print()
    print('=== testing ec2 ===')
    output_instances = ec2('describe-instances',
                            region='us-west-2',
                            query='Reservations[].Instances[].[InstanceId,Tags[?Key==`Name`].Value]',
                            verbose=True)
    dreambox.utils.print_structure(output_instances)
    print('=== end testing ec2 ===')
    print()
    print('==== testing autoscaling ===')
    autoscaling_groups = autoscaling('describe-auto-scaling-groups',
                                     verbose=False,
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
                             dry_run=False,
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
    print('==== testing json_to_pyobj ====')
    json_object = json.loads('{"a": 1, "b": {"c": {"d": 2}}}')

    py_json = json_to_pyobj(json_object)
    dreambox.utils.print_structure(py_json)
    print('py_json.b.c.d = %s' % py_json.b.c.d)

    json_obj = json.loads('[{"a": {"c": {"e": 1}}}, {"b": 2}]')
    py_json = json_to_pyobj(json_obj)
    dreambox.utils.print_structure(py_json[0]['a'].c.e)
    print('==== end testing json_to_pyobj ====')

