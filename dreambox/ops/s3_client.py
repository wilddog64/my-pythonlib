import dreambox.aws.s3 as s3
import dreambox.utils

def get_backupset_bucketnames(envroot='west-backup-databag',
                              ownerroot='',
                              region='us-west-2',
                              verbose=True):
    '''
get_backupset_bucketnames will return all the backup bucket name whose tagging key is OWNNER and
tagging value is UPDATED.  The function takes the following parameters,

* envroot is the root of the backup set
* ownerroot is a owner of that backup set root
* region is an AWS region
    '''
    buckets = s3.list_buckets(region=region,
                              filterby=envroot,
                              verbose=verbose)
    if verbose:
        dreambox.utils.print_structure(buckets)

    backuplist = []
    owner, updated = ('', '')
    for bucket in buckets:
        if bucket:
            tags = s3.get_bucket_tagging(region=region,
                                        bucket=bucket['Name'],
                                        verbose=verbose)
            if tags:
                tags = tags['TagSet']
                # dreambox.utils.print_structure(tags)
                for tag in tags:
                    if tag and tag['Key'] == 'UPDATED':
                        updated = tag['Value']
                    if tag and tag['Key'] == 'OWNER':
                        owner = tag['Value']

                if owner and ownerroot in owner or ownerroot == '':
                    backuplist.append({'bucket': bucket['Name'], 'owner': owner, 'updated': updated})
    backuplist = sorted(backuplist, key=lambda bucket: bucket['updated']) 
    return backuplist


if __name__ == '__main__':
    get_backupset_bucketnames(verbose=False)
