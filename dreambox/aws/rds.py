from __future__ import print_function
import dreambox.aws.core as aws
import dreambox.utils
import datetime
import dateutil.parser 

def describe_rds_snapshots(profile='', region='us-east-1', env_prefix=''):
    '''
get_rds_snapshots will return a list of RDS database snapshots to a
caller. The function takes the following parameters:

* profile - an aws profile that provide credential information.  If this is
            None, it will first look at a default profile setting at
            ~/.aws/config. If it cannot find default profile, it will use node
            IAM profile if there's one exist for a given node.
* regions - a list of regions to search for a target environment. If this is
            None, it will search for us-east-1 and us-west-2.
* env_prefix - an environment prefix like stage1, ..., stage9
    '''
    db_snapshots = []
    if env_prefix != '':
        db_snapshots = [s for s in aws.rds('describe-db-snapshots', profile=profile, region='us-east-1')['DBSnapshots'] 
                if env_prefix.lower() in s['DBSnapshotIdentifier'].lower()]
    else:
        db_snapshots = [s for s in aws.rds('describe-db-snapshots', profile=profile, region='us-east-1')['DBSnapshots']]

    return db_snapshots

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
    db_snapshots = describe_rds_snapshots(profile=profile,
                                          region=region,
                                          env_prefix=env_prefix)
    return sorted(db_snapshots, key=)

if __name__ == '__main__':
    print('--- testing describe_rds_snapshots ---')
    rds_db_snapshots = describe_rds_snapshots(env_prefix='playbackup')
    dreambox.utils.print_structure(rds_db_snapshots)
    print('--- testing describe_rds_snapshots ---')
