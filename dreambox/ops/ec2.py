from __future__ import print_function
from dreambox.aws.core import aws_ec2cmd
import dreambox.utils
import sys

def get_ec2_hosts_for_stage(profile=None, regions=None, stage=None):
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

    def make_hash_from_ec2tag(a_list, stage=None):
        my_hash = {}

        for elem in a_list:
            ec2_tag = elem[-1]
            if ec2_tag:
                tag_name = ec2_tag[0]['Value'].lower()
                if ec2_tag[0:1] and not stage is None and stage.lower() in tag_name.lower():
                    my_hash[tag_name] = elem[0:2]
                elif ec2_tag[0:1] and stage is None:
                    my_hash[tag_name] = elem[0:2]

        return my_hash


    inst_qry = 'Reservations[].Instances[].[PublicDnsName,PublicIpAddress,Tags[?Key==`Name`]]'
    instances = {}
    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    for region in regions:
        region_instances = aws_ec2cmd(ec2profile=profile,
                                      ec2region=region,
                                      subcmd='describe-instances',
                                      query=inst_qry)
        # dreambox.utils.print_structure(region_instances)
        instances[region] = make_hash_from_ec2tag(region_instances, stage)

    return instances

if __name__ == '__main__':
    ec2_instances = get_ec2_hosts_for_stage(stage='stage3')
    dreambox.utils.print_structure(ec2_instances)