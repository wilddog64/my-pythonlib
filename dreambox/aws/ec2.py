from __future__ import print_function
import dreambox.aws.core as aws
from dreambox.aws.core import aws_ec2cmd
import dreambox.utils
import types
import json

  
def get_ec2_hosts_for_stage(profile='', regions=None, stage=None):
    '''
get_ec2_hosts_for_stage  will return ec2 instance information for a given
stage environment.  This function takes the following parameters,

* profile - an aws profile that provide credential information.  If this is
            None, it will first look at a default profile setting at
            ~/.aws/config. If it cannot find default profile, it will use node
            IAM profile if there's one exist for a given node.
* regions - a list of regions to search for a target environment. If this is
            None, it will search for us-east-1 and us-west-2.
* stage - a stage environment to look for
    '''

    def make_hash_from_ec2tag(a_list, stage):
        my_hash = {}

        for elem in a_list:
            ec2_tag = elem[-1]
            if ec2_tag:
                tag_name = ec2_tag[0].lower()
                if ec2_tag[0:1] and not stage is None and stage.lower() in tag_name.lower():
                    my_hash[tag_name] = elem[0:2]
                elif ec2_tag[0:1] and stage is None:
                    my_hash[tag_name] = elem[0:2]

        return my_hash


    inst_qry = 'Reservations[].Instances[].[PublicDnsName,PublicIpAddress,Tags[?Key==`Name`].Value]'
    instances = {}
    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    for region in regions:
        region_instances = aws.ec2('describe-instances',
                                   profile=profile,
                                   region=region,
                                   query=inst_qry)
        # dreambox.utils.print_structure(region_instances)
        instances[region] = make_hash_from_ec2tag(region_instances, stage)

    return instances

def describe_instances(profile=None, region=None, filterby=None, **options):
    '''
describe_instances is a function that return all the instances for a give region.
The function takes the following parameters,

* profile is an AWS profile setting stored at ~/.aws/config
* region is an AWS region
* filterby is a function that filter through a list of instances
* **options is any valid aws describe-instances command line options
    '''

    instances = aws_ec2cmd(ec2profile=profile,
                           ec2region=region,
                           subcmd='describe-instances',
                           verbose=True,
                           **options)
    if filterby is not None and type(filterby) is types.FunctionType:
        instances = filter(filterby, instances)

    return instances


def list_instances_securitygroups(profile=None,
                                  region='',
                                  filterby_tag=None,
                                  filterby_securitygroup=None):
    '''
list_instances_securitygroups is a function that will return all instances with
security group for a given region.  The function takes these parameters,

* profile is an AWS profile defined in ~/.aws/config.  For AWS instances, this
  is not required
* region is an AWS region that this function will work on
* fiterby_tag is a filter function that searches instances by looking at particular tag
* filteryby_security_group is a filter function that looks for a particular scurity group
  asscoiate with instances

if filterby_tag and filterby_security_group are not provided, then return all instances
with security groups
    '''
    # a query that return InstanceId, Tag, and SecurityGroups
    instance_query = 'Reservations[].Instances[].[Tags[?Key==`Name`].Value,InstanceId,SecurityGroups[],State.Name]'
    instances = describe_instances(profile=profile,
                                   region=region,
                                   filterby=filterby_tag,
                                   query=instance_query)
    if filterby_securitygroup is not None:
        instances = filter(filterby_securitygroup, instances)

    return instances


def modify_instance_attribute(profile=None,
                              region=None,
                              dry_run=False,
                              verbose=True,
                              **kwargs):
    '''
modify_instance_attribute is a function that allows to modify attributes
for a given AWS instance.  The function takes the following parameters,


* profile is an AWS profile defined in ~/.aws/config.  For AWS instances, this
  is not required
* region is an AWS region that this function will work on
* **kwargs is any valid aws ec2 modify_instance_attributes options
    '''
    aws_ec2cmd(ec2profile=profile,
               ec2region=region,
               subcmd='modify-instance-attribute',
               dry_run=dry_run,
               verbose=verbose,
               **kwargs)


if __name__ == '__main__':
    ec2_instances = get_ec2_hosts_for_stage(stage='stage3')
    dreambox.utils.print_structure(ec2_instances)

    print('--- testing describe_instances ---')
    instance_query = 'Reservations[].Instances[].[Tags[?Key==`Name`].Value[],PrivateIpAddress,PrivateDnsName]'
    filter_expression = 'pp-thor-edex'
    def filterby(x):
        if x[0] is not None:
            return filter_expression in x[0][0]
    node_instances = describe_instances(profile='dreamboxdev',
                                        region='us-east-1',
                                        filterby=filterby,
                                        query=instance_query)
    dreambox.utils.print_structure(node_instances)
    print('--- end testing describe_instances ---')

    print('--- testing list_instances_securitygroups ---')
    filter_expression = 'pp-'
    securitygroup_filter = 'sg-a132cfc6'
    def filterby_tag(x):
        if x[0] is not None:
            return filter_expression in x[0][0] and x[3] == 'running'
    def filter_securitygroup(x):
        if x[2] is not None:
            return securitygroup_filter.lower() not in x[2][0]['GroupId'].lower()

    return_instances = list_instances_securitygroups(profile='dreamboxdev',
                                                     region='us-east-1',
                                                     filterby_tag=filterby_tag,
                                                     filterby_securitygroup=filter_securitygroup)
    dreambox.utils.print_structure(return_instances)
    print('--- end testing list_instances_securitygroups ---')
    print()
    print('--- testing modify_instance_attribute ---')
    modify_instance_attribute(profile='dreamboxdev',
                              region='us-east-1',
                              dry_run=True,
                              verbose=True,
                              instance_id='i-7ddc1081',
                              group='sg-a132cfc6')
