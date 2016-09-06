from __future__ import print_function
from collections import defaultdict
import dreambox.aws.rds as rds
import dreambox.utils
import dateutil.parser
import datetime

def get_latest_rds_snapshot(profile='', region='us-east-1', env_prefix=''):
    '''
get_lastest_rds_snapshot is a function that will return a latest created snapshot
base on the SnapshotCreateTime. This function takes the following parameters,

* profile - an aws profile that provide credential information.  If this is
	    None, it will first look at a default profile setting at
	    ~/.aws/config. If it cannot find default profile, it will use node
	    IAM profile if there's one exist for a given node.
* regions - a list of regions to search for a target environment. If this is
	    None, it will search for us-east-1 and us-west-2.
* env_prefix - an environment prefix like stage1, ..., stage9
    '''

    return get_sorted_rds_snapshots(profile=profile, region=region, env_prefix=env_prefix)[0]

def get_sorted_rds_snapshots(profile='', region='us-east-1', env_prefix=''):
    '''
get_sorted_rds_snapshots is a function return a list of ordered rds snapshots based on their creatioin time 
(base on SnapshotCreateTime). The function takes the following parameters

* profile - an aws profile that provide credential information.  If this is
	    None, it will first look at a default profile setting at
	    ~/.aws/config. If it cannot find default profile, it will use node
	    IAM profile if there's one exist for a given node.
* regions - a list of regions to search for a target environment. If this is
	    None, it will search for us-east-1 and us-west-2.
* env_prefix - an environment prefix like stage1, ..., stage9
    '''
    db_snapshots = rds.describe_rds_snapshots(profile=profile,
					      region=region,
					      env_prefix=env_prefix)
    sort_key = 'SnapshotCreateTime'
    decorated = []
    decorated = [(dateutil.parser.parse(dict_[sort_key]), dict_) for dict_ in db_snapshots]
    decorated.sort(reverse=True)

    return [dict_ for (key, dict_) in decorated]

def get_g2_rds_snapshots(profile='', region='us-east-1', env_prefix='production-g2'):
    '''
get_g2_rds_snapshots is a function that returns a hash of arrays whose key is a day stamp

* profile - an aws profile that provide credential information.  If this is
	    None, it will first look at a default profile setting at
	    ~/.aws/config. If it cannot find default profile, it will use node
	    IAM profile if there's one exist for a given node.
* regions - a list of regions to search for a target environment. If this is
	    None, it will search for us-east-1 and us-west-2.
* env_prefix - an environment prefix like stage1, ..., stage9
    '''
    snapshots = get_sorted_rds_snapshots(profile=profile, region=region, env_prefix=env_prefix)

    # create a hash of arrays whose key is the time of the snapshots created
    current_year = datetime.datetime.now().year
    hash_table = {}
    for snapshot in snapshots:
        if str(current_year) in snapshot['DBSnapshotIdentifier']:
            start_pos = snapshot['DBSnapshotIdentifier'].index(str(current_year))
            key       = snapshot['DBSnapshotIdentifier'][start_pos:-6]
            hash_table.setdefault(key, []).append(snapshot)

    return hash_table

if __name__ == '__main__':
    print('--- testing get_latest_rds_snapshot')
    rds_snapshots = get_latest_rds_snapshot(env_prefix='playbackup')
    dreambox.utils.print_structure(rds_snapshots)
    print('--- testing get_latest_rds_snapshot')
    print('')
    print('--- testing get_sorted_rds_snaphots')
    sorted_snapshots = get_sorted_rds_snapshots(region='us-east-1', env_prefix='production-g2')
    dreambox.utils.print_structure(sorted_snapshots)
    print('--- testing get_sorted_rds_snaphots')
    print('')
    print('--- testing get_g2_rds_snapshots')
    g2_rds_snapshots = get_g2_rds_snapshots(region='us-east-1')
    dreambox.utils.print_structure(g2_rds_snapshots)
    print('--- testing get_g2_rds_snapshots')

