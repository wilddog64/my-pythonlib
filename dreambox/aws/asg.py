from dreambox.aws.core import *
import dreambox.utils

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
    hashes = dreambox.utils.make_hash_of_hashes(get_all_asgs(ec2profile,
                                                             ec2region,
                                                             **options))
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

if __name__ == '__main__':
    from dreambox.aws.lib import *
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

