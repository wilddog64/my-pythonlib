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

def get_latest_g2_snapshot_older_than_play(profile='', region=''):
    '''
get_latest_g2_snapshot_older_than_play is a function that will return a list of g2 rds snapshots
that the latest one but older then current play rds backup. The function takes the following
parameters,

* profile - an aws profile that provide credential information.  If this is
	    None, it will first look at a default profile setting at
	    ~/.aws/config. If it cannot find default profile, it will use node
	    IAM profile if there's one exist for a given node.
* regions - a list of regions to search for a target environment. If this is
	    None, it will search for us-east-1 and us-west-2.
    '''
    latest_playbackup = get_latest_rds_snapshot(profile=profile, region=region, env_prefix='playbackup')
    playbackup_create_time = dateutil.parser.parse(latest_playbackup['SnapshotCreateTime'])
    g2_rds_snapshots = get_g2_rds_snapshots(profile=profile, region=region)
    g2_timestamp_key = str((playbackup_create_time - datetime.timedelta(hours=24)).date())
    latest_g2_snapshot = None
    while True:
        if g2_timestamp_key in g2_rds_snapshots:
            latest_g2_snapshot = g2_rds_snapshots[g2_timestamp_key]
            break
        g2_timestamp_key = str((dateutil.parser.parse(g2_timestamp_key - datetime.timedelta(days=1))).date())

    return latest_g2_snapshot

if __name__ == '__main__':
    print('--- testing get_latest_rds_snapshot')
    rds_snapshots = get_latest_rds_snapshot(env_prefix='playbackup')
    dreambox.utils.print_structure(rds_snapshots)
    print('--- testing get_latest_rds_snapshot')
    print('')
    print('--- testing get magneto_snapshot ---')
    rds_snapshots = get_latest_rds_snapshot(region='us-west-2', env_prefix='magnetobackup')
    dreambox.utils.print_structure(rds_snapshots)
    print('--- testing get magneto_snapshot ---')
    print('')
    print('--- testing get apibackup_snapshot ---')
    rds_snapshots = get_latest_rds_snapshot(region='us-west-2', env_prefix='apibackup')
    dreambox.utils.print_structure(rds_snapshots)
    print('--- testing get apibackup_snapshot')
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
    print('')
    print('--- testing get_latest_g2_snapshot_older_than_play ---')
    latest_g2_snapshot = get_latest_g2_snapshot_older_than_play(region='us-east-1')
    dreambox.utils.print_structure(latest_g2_snapshot)
    print('--- testing get_latest_g2_snapshot_older_than_play ---')

