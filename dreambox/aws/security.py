from __future__ import print_function
from dreambox.aws.core import aws_ec2cmd
from dreambox.aws.core import aws_rdscmd
from dreambox.aws.core import aws_redshiftcmd
from dreambox.aws.core import aws_ecachecmd
import dreambox.utils
import sys


def get_all_ec2_security_groups(ec2profile=None,
                                regions=None,
                                query=None,
                                filterby=None):

    if query is None:
        query = 'SecurityGroups[].GroupName'
    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    ec2_results = []
    ec2_result = {}
    for region in regions:
        ec2_result[region] = aws_ec2cmd(ec2profile,
                                        region,
                                        subcmd='describe-security-groups',
                                        query=query)
        ec2_results.extend(ec2_result)

    return dreambox.utils.filter_list_by(ec2_result, myfilter=filterby)


def get_all_elasticcache_security_groups(ec2profile=None,
                                         regions=None,
                                         query=None,
                                         filterby=None):

    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    if query is None:
        query = 'CacheSecurityGroups[].EC2SecurityGroups[].EC2SecurityGroupName'
    ecache_results = []
    ecache_result = {}
    for region in regions:
        ecache_result[region] = aws_ecachecmd(ec2profile,
                                              region,
                                              ecache_subcmd='describe-cache-security-groups',
                                              query=query)
        ecache_results.extend(ecache_result)

    return dreambox.utils.filter_list_by(ecache_result, myfilter=filterby)


def get_all_rds_security_groups(ec2profile=None,
                                regions=None,
                                query=None,
                                filterby=None):

    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    if query is None:
        query = 'DBSecurityGroups[].EC2SecurityGroups[].EC2SecurityGroupName'

    rds_results = []
    rds_result = {}
    for region in regions:
        rds_result[region] = aws_rdscmd(ec2profile,
                                        region,
                                        rds_subcmd='describe-db-security-groups',
                                        query=query)
        rds_results.extend(rds_result)

    return dreambox.utils.filter_list_by(rds_result, myfilter=filterby)


def get_all_rds_ingress_rules_for_stage(ec2profile=None,
                                        regions=None,
                                        filterby=None,
                                        dry_run=False):
    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    rds_qry = 'DBSecurityGroups[].[DBSecurityGroupName,EC2SecurityGroups[].EC2SecurityGroupName]'
    hashtable = {}
    for region in regions:
        hashtable[region] = aws_rdscmd(aws_profile=ec2profile,
                                       aws_region=region,
                                       rds_subcmd='describe-db-security-groups',
                                       dry_run=dry_run,
                                       query=rds_qry)

    return dreambox.utils.create_hashtable_from_hashes2(hashtable, filterby)


def revoke_all_rds_ingress_rules_for_stage(ec2profile=None,
                                           regions=None,
                                           filterby=None,
                                           dry_run=False):
    ingress_rules_to_delete = get_all_rds_ingress_rules_for_stage(ec2profile,
                                                                  regions,
                                                                  filterby)
    for region, security_groups in ingress_rules_to_delete.items():
        for security_group_name, ingress_rules in security_groups.items():
            for ingress_rule in ingress_rules:
                aws_rdscmd(aws_profile=ec2profile,
                           aws_region=region,
                           rds_subcmd='revoke-db-security-group-ingress',
                           dry_run=dry_run,
                           verbose=True,
                           ec2_security_group_name=security_group_name,
                           db_security_group_name=ingress_rule)
                print('ingress rule {} for {} is revoked'.format(ingress_rule,
                                                                 security_group_name),
                      file=sys.stderr)


def get_all_redshift_ingress_rules_for_stage(ec2profile=None,
                                             regions=None,
                                             filterby=None,
                                             dry_run=False):
    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    redshift_qry = 'ClusterSecurityGroups[].[ClusterSecurityGroupName,EC2SecurityGroups[].EC2SecurityGroupName]'

    hashtable = {}
    for region in regions:
        hashtable[region] = aws_redshiftcmd(aws_profile=ec2profile,
                                            aws_region=region,
                                            redshift_subcmd='describe-cluster-security-groups',
                                            dry_run=dry_run,
                                            query=redshift_qry)

    return dreambox.utils.create_hashtable_from_hashes2(hashtable, filterby)


def revoke_all_redshift_ingress_rules_for_stage(ec2profile=None,
                                                regions=None,
                                                filterby=None,
                                                dry_run=None):
    ingress_rules_to_delete = get_all_redshift_ingress_rules_for_stage(ec2profile,
                                                                       regions,
                                                                       filterby)
    for region, security_groups in ingress_rules_to_delete.items():
        for security_group_name, ingress_rules in security_groups.items():
            for ingress_rule in ingress_rules:
                aws_redshiftcmd(aws_profile=ec2profile,
                                aws_region=region,
                                redshift_subcmd='revoke-cluster-security-group-ingress',
                                dry_run=dry_run,
                                verbose=True,
                                ec2_security_group_name=security_group_name,
                                cluster_security_group_name=ingress_rule)
                print('ingress rule {} for {} is revoked'.format(ingress_rule,
                                                                 security_group_name),
                      file=sys.stderr)


def get_all_ec2_ingress_rules_for_stage(ec2profile=None,
                                        regions=None,
                                        filterby=None,
                                        dry_run=False):
    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    ec2_qry = 'SecurityGroups[].[GroupName,IpPermissions[].[ToPort,IpProtocol,IpRanges[].CidrIp]][]'

    hashtable = {}
    for region in regions:
        hashtable[region] = aws_ec2cmd(ec2profile=ec2profile,
                                       ec2region=region,
                                       subcmd='describe-security-groups',
                                       dry_run=dry_run,
                                       query=ec2_qry)

    return dreambox.utils.create_hashtable_from_hashes(hashtable, filterby)



def revoke_all_ec2_ingress_rules_for_stage(ec2profile=None,
                                           regions=None,
                                           filterby=None,
                                           dry_run=None):
    ingress_rules_to_delete = get_all_ec2_ingress_rules_for_stage(ec2profile,
                                                                  regions,
                                                                  filterby)
    for region, security_groups in ingress_rules_to_delete.items():
        for security_group_name, ingress_rules in security_groups.items():
            for ingress_rule in ingress_rules:
                aws_ec2cmd(ec2profile=ec2profile,
                           ec2region=region,
                           subcmd='revoke-security-group-ingress',
                           dry_run=dry_run,
                           verbose=True,
                           group_name=security_group_name,
                           port=ingress_rule[0],
                           protocol=ingress_rule[1])
                print('ingress rule {} for {} is revoked'.format(ingress_rule,
                                                                 security_group_name),
                      file=sys.stderr)


def get_all_elasticache_ingress_rules_for_stage(ec2profile=None,
                                                regions=None,
                                                filterby=None,
                                                verbose=False,
                                                dry_run=False):
    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    elasticache_qry = 'CacheSecurityGroups[].[CacheSecurityGroupName,EC2SecurityGroups[].EC2SecurityGroupName,OwnerId]'

    hashtable = {}
    for region in regions:
        hashtable[region] = aws_ecachecmd(aws_profile=ec2profile,
                                          aws_region=region,
                                          ecache_subcmd='describe-cache-security-groups',
                                          dry_run=dry_run,
                                          query=elasticache_qry)
    return_rst = None
    if not dry_run:
        return_rst = dreambox.utils.create_hashtable_from_hashes2(hashtable, filterby)
    else:
        print('dry_run mode', file=sys.stderr)

    return return_rst

def get_all_redshift_security_groups(ec2profile=None,
                                     regions=['us-east-1', 'us-west-2'],
                                     filterby=None):

    redshift_results = []
    redshift_result = {}
    for region in regions:
        redshift_result[region] = aws_redshiftcmd(ec2profile,
                                                  region,
                                                  redshift_subcmd='describe-cluster-security-groups',
                                                  query='ClusterSecurityGroups[].EC2SecurityGroups[].EC2SecurityGroupName')
        redshift_results.extend(redshift_result)

    return dreambox.utils.filter_list_by(redshift_result, myfilter=filterby)


def get_all_security_groups(my_ec2profile=None,
                            my_regions=['us-east-1', 'us-west-2'],
                            my_filterby=None):
    results = {}
    results['ec2'] = get_all_ec2_security_groups(ec2profile=my_ec2profile,
                                                 regions=my_regions,
                                                 filterby=my_filterby)
    results['elasticcache'] = get_all_elasticcache_security_groups(ec2profile=my_ec2profile,
                                                                   regions=my_regions,
                                                                   filterby=my_filterby)
    results['rds'] = get_all_rds_security_groups(ec2profile=my_ec2profile,
                                                 regions=my_regions,
                                                 filterby=my_filterby)
    results['redshift'] = get_all_redshift_security_groups(ec2profile=my_ec2profile,
                                                           regions=my_regions,
                                                           filterby=my_filterby)
    return results

def delete_security_groups(ec2profile=None,
                           regions=None,
                           my_filterby='stage3',
                           dry_run=False,
                           **options):

    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    security_groups_to_delete = get_all_security_groups(ec2profile,
                                                        regions,
                                                        my_filterby)
    for cmdcat, regions in security_groups_to_delete.items():
        for region, security_groups in regions.items():
            for security_group in security_groups:
                if dry_run:
                    if cmdcat == 'ec2':
                        aws_ec2cmd(ec2profile=ec2profile,
                                   ec2region=region,
                                   subcmd='delete-security-group',
                                   dry_run=dry_run,
                                   group_name=security_group)
                    elif cmdcat == 'elasticcache':
                        aws_ecachecmd(aws_profile=ec2profile,
                                      aws_region=region,
                                      ecache_subcmd='delete-cache-security-group',
                                      cache_security_group_name=security_group)
                    elif cmdcat == 'rds':
                        aws_rdscmd(aws_profile=ec2profile,
                                   aws_region=region,
                                   rds_subcmd='delete-db-security-group',
                                   dry_run=dry_run,
                                   db_security_group_name=security_group)
                    elif cmdcat == 'redshift':
                        aws_redshiftcmd(aws_profile=ec2profile,
                                        aws_region=region,
                                        subcmd='delete-cluster-security-group',
                                        dry_run=dry_run,
                                        cluster_security_group_name=security_group)


def revoke_all_elasticache_ingress_rules_for_stage(ec2profile=None,
                                                   regions=None,
                                                   filterby=None,
                                                   verbose=False,
                                                   dry_run=False):
    ingress_rules_to_delete = get_all_elasticache_ingress_rules_for_stage(ec2profile,
                                                                          regions,
                                                                          filterby,
                                                                          verbose=verbose)
    for region, security_groups in ingress_rules_to_delete.items():
        for security_group_name, ingress_rules in security_groups.items():
                aws_ecachecmd(aws_profile=ec2profile,
                              aws_region=region,
                              ecache_subcmd='revoke-cache-security-group-ingress',
                              dry_run=dry_run,
                              verbose=verbose,
                              ec2_security_group_name=security_group_name,
                              cache_security_group_name=ingress_rules[0][0],
                              ec2_security_group_owner_id=ingress_rules[1])
                print('ingress rule {} for {} is revoked'.format(ingress_rules[0][0],
                                                                 security_group_name),
                      file=sys.stderr)


def revoke_all_ingress_rules(ec2profile=None,
                             ec2regions=None,
                             filterby=None,
                             dry_run=False,
                             verbose=False):
    revoke_all_rds_ingress_rules_for_stage(ec2profile,
                                           ec2regions,
                                           filterby,
                                           dry_run)
    revoke_all_redshift_ingress_rules_for_stage(ec2profile,
                                                ec2regions,
                                                filterby,
                                                dry_run)
    revoke_all_elasticache_ingress_rules_for_stage(ec2profile,
                                                   ec2regions,
                                                   filterby,
                                                   dry_run,
                                                   verbose)
    revoke_all_ec2_ingress_rules_for_stage(ec2profile,
                                           ec2regions,
                                           filterby,
                                           dry_run)

if __name__ == '__main__':
    print('result from get_all_ec2_security_groups')

    print('================================================', file=sys.stderr)
    my_result = get_all_ec2_security_groups()
    dreambox.utils.print_structure(my_result)

    print('filter by stage2')
    print('================================================', file=sys.stderr)
    filter_result = get_all_ec2_security_groups(filterby='Stage2')
    dreambox.utils.print_structure(filter_result)
    print('end of get_all_ec2_security_groups')
    print('================================================', file=sys.stderr)

    print('result from get_all_elasticcache_security_groups')
    print('================================================', file=sys.stderr)
    my_result = get_all_elasticcache_security_groups()
    dreambox.utils.print_structure(my_result)
    print('filter by stage2')
    my_result = get_all_elasticcache_security_groups(filterby='stage3')
    dreambox.utils.print_structure(my_result)
    print('end of get_all_elasticcache_security_groups')
    print('================================================', file=sys.stderr)

    print('result from get_all_rds_security_groups')
    print('================================================', file=sys.stderr)
    my_result = get_all_rds_security_groups()
    dreambox.utils.print_structure(my_result)
    print('filter by stage2')
    my_result = get_all_rds_security_groups(filterby='stage3')
    dreambox.utils.print_structure(my_result)
    print('end of get_all_rds_security_groups')
    print('================================================', file=sys.stderr)

    print('result from get_all_redshift_security_groups')
    print('================================================', file=sys.stderr)
    my_result = get_all_redshift_security_groups()
    dreambox.utils.print_structure(my_result)
    print('filter by stage3')
    result = get_all_redshift_security_groups(filterby='stage3')
    dreambox.utils.print_structure(my_result)
    print('end of get_all_redshift_security_groups')
    print('================================================', file=sys.stderr)

    print('result from get_all_security_groups')
    print('================================================', file=sys.stderr)
    my_result = get_all_security_groups()
    dreambox.utils.print_structure(my_result)
    print('result from get_all_security_groups filtered by stage3')
    my_result = get_all_security_groups(my_filterby='stage3')
    dreambox.utils.print_structure(my_result)
    print('end of get_all_security_groups')
    print('================================================', file=sys.stderr)

    print('result from get_all_rds_ingress_rules_for_stage', file=sys.stderr)
    print('================================================', file=sys.stderr)
    result = get_all_rds_ingress_rules_for_stage(ec2profile='mgmt',
                                                 filterby='stage3')
    dreambox.utils.print_structure(result)
    print('end of get_all_rds_ingress_rules_for_stage', file=sys.stderr)
    print('================================================', file=sys.stderr)

    print('result from get_all_redshift_ingress_rules_for_stage', file=sys.stderr)
    print('================================================', file=sys.stderr)
    result = get_all_redshift_ingress_rules_for_stage(ec2profile='mgmt',
                                                      filterby='stage3')
    dreambox.utils.print_structure(result)
    print('end of get_all_redshift_ingress_rules_for_stage', file=sys.stderr)
    print('================================================', file=sys.stderr)

    print('result from get_all_ec2_ingress_rules_for_stage', file=sys.stderr)
    print('================================================', file=sys.stderr)
    result = get_all_ec2_ingress_rules_for_stage(ec2profile='mgmt',
                                                 filterby='stage3')
    dreambox.utils.print_structure(result)
    print('end of get_all_ec2_ingress_rules_for_stage', file=sys.stderr)
    print('================================================', file=sys.stderr)

    print('result from get_all_elasticache_ingress_rules_for_stage', file=sys.stderr)
    print('================================================', file=sys.stderr)
    result = get_all_elasticache_ingress_rules_for_stage(ec2profile='mgmt',
                                                         filterby='stage3')
    dreambox.utils.print_structure(result)
    print('end of get_all_elasticache_ingress_rules_for_stage', file=sys.stderr)
    print('================================================', file=sys.stderr)

    print('testing revoke_all_ingress_rules in dry run ode with filter set to stage3')
    print('==========================================================================')
    revoke_all_ingress_rules(filterby='stage3', dry_run=True)
    print('end of testing revoke_all_ingress_rules')
    print('==========================================================================')
