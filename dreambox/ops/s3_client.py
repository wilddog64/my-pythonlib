import dreambox.aws.s3 as s3
import dreambox.utils
import dreambox.json.core as json

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


def get_backupsets_from_all_regions(ownerroot='', regions=None, verbose=False):
    '''
get_backupsets_from_all_regions is a function that will return all the backup sets
from all known region.  The function takes the following parameters,

* ownerroot is an owner of the backup sets
* regions is a hash that describes the backup set regions. This is a python dictionary object
  that has the following format

    {
       region: envroot
    }

    where region is a valid AWS region and
          envroot is a s3 bucket suffix

when function call is successful, a dictionary object is return with the following format

    region: [
      { 'bucket': bucket_name,
        'owner': stage_environment,
        'update': last_time_backupset_was_made}
    ]
    '''
    # if regions is None, then we create a dict object where
    # key is an AWS region, and value is region's databag
    if regions is None:
        regions = {'us-east-1': 'east-backup-databag',
                   'us-west-2': 'west-backup-databag',}

    bucket_backupsets = {}
    for region, envroot in regions.items():
        bucket_backupsets[region] = get_backupset_bucketnames(envroot=envroot,
                                                              ownerroot=ownerroot,
                                                              region=region,
                                                              verbose=verbose)
    return bucket_backupsets


def show_regional_backupsets(args=None):
    owner = args.owner
    regions = json.json2py(args.regions)
    verbose = dreambox.utils.to_bool(args.verbose)

    if owner is None:
       owner = ''

    backupsets = get_backupsets_from_all_regions(ownerroot=owner,
                                                 regions=regions,
                                                 verbose=verbose)
    dreambox.utils.print_structure(backupsets)

if __name__ == '__main__':
    backup_list = get_backupset_bucketnames(verbose=False)
    dreambox.utils.print_structure(backup_list)
    for backup in backup_list:
        print("%s\t%s\t%s" % (backup['bucket'], backup['owner'], backup['updated']))

    print('==== testing get_backupsets_from_all_regions ===')
    backupsets = get_backupsets_from_all_regions()
    dreambox.utils.print_structure(backupsets)
    print('==== end testing get_backupsets_from_all_regions ===')
