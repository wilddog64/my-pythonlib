from __future__ import print_function

from funcy.colls import select
import dreambox.utils
import sys
import re
from distutils.version import LooseVersion

import dreambox.aws.core as aws

def get_buckets(profile='',
                region='',
                filterby=None,
                dry_run=False,
                verbose=False):
    '''
get_buckets will return all the buckets exists in AWS s3 storage.  The function
takes these parameters,

*  profile: a profile that aws command will reference
*  region: which region aws is going to tackle
*  dry_run: checks whether you have the required permissions for the
   action, without actually making the request. Using this option
   will result in one of two possible error responses. If you have
   the required permissions the error response will be DryRunOperation.
   Otherwise it will be UnauthorizedOperation

    '''

    s3_buckets = aws.s3api('list-buckets',
                           profile=profile,
                           region=region,
                           dry_run=dry_run,
                           verbose=verbose)
    return_rst = s3_buckets['Buckets']
    if filterby is not None:
       return_rst = select(lambda bucket: filterby.lower() in bucket['Name'],
                           return_rst)

    item_table = {}
    for item in return_rst:
        Key = item['Name']
        Value = item['CreationDate']
        if Key:
            item_table[Key] = Value

    return item_table


def get_bucket_tags(profile='',
                    region='',
                    bucket=None,
                    filterby=None,
                    dry_run=False,
                    verbose=False):
    '''
get_bcuket_tags will return tag sets for all the s3 bucket or if filterby is
provided, return filtered bucket tags back to caller.  The function takes these
parameters,


*  profile: a profile that aws command will reference
*  region: which region aws is going to tackle
*  bucket: name of the s3 bucket that this function uses to find a tagset
*  dry_run: checks whether you have the required permissions for the
   action, without actually making the request. Using this option
   will result in one of two possible error responses. If you have
   the required permissions the error response will be DryRunOperation.
   Otherwise it will be UnauthorizedOperation
    '''

    s3_bucket_tagset = aws.s3api('get-bucket-tagging',
                                 profile=profile,
                                 region=region,
                                 dry_run=dry_run,
                                 verbose=verbose,
                                 bucket=bucket)

    s3_tagset = {}
    for tagset in s3_bucket_tagset['TagSet']:
        Key = tagset['Key']
        Value = tagset['Value']
        if Key:
            s3_tagset[Key] = Value

    return s3_tagset


def create_or_update_s3bucket(profile='',
                              region='us-west-2',
                              bucket_name=None,
                              key=None,
                              value=None,
                              dry_run=False,
                              verbose=False):

    print('testing')
    tagset = ''' { "TagSet": { "Key": "%s", "Value": "%s" } }''' % (key, value)
    aws.s3api('put-bucket-tagging',
              profile=profile,
              region=region,
              dry_run=dry_run,
              verbose=verbose,
              bucket=bucket_name,
              tagging=tagset)

    return tagset

def get_s3nexus_artifacts(bucket='dreambox-deployment-files',
                          type='releases',
                          key='Nexus',
                          branch=None,
                          version=None):
   # construct an s3 path toward the valid s3 bucket
    path = None
    if version is None: # if version is not pass in then points to the branch
       path = 's3://%s/%s/%s/com/dreambox/dbl-%s-main/' % (bucket, key, type, branch)
    else:  # otherwise return what's in side a specific version
       path = 's3://%s/%s/%s/com/dreambox/dbl-%s-main/%s/' % (bucket, key, type, branch, version)

    # filter out all the noise strings and grab only version numbers to store in versions array
    output = None
    versions = []
    if path is not None:
       output = aws.s3('ls', path)
       m = re.compile(r'\s+PRE\s|\/$')
       for line in output:
          if m.match(line):
             line = m.sub('', line).rstrip()
             versions.append(line)

    # return a sorted versions in descending order
    return sorted([LooseVersion(v).vstring for v in versions], reverse=True)


if __name__ == '__main__':

    print('testing get_bucket', file=sys.stderr)
    print('------------------')
    buckets = get_buckets(region='us-west-2', filterby='backup-databag')
    dreambox.utils.print_structure(buckets)
    print('end testing get_bucket', file=sys.stderr)
    print('------------------')

    print('testing get_bucket_tags', file=sys.stderr)
    print('------------------')
    bucket_tagset = get_bucket_tags(region='us-west-2', bucket='03west-backup-databag')
    dreambox.utils.print_structure(bucket_tagset)
    print('end testing get_bucket_tags', file=sys.stderr)
    print('------------------')

    print('testing create_or_update_s3bucket', file=sys.stderr)
    print('------------------')
    create_or_update_s3bucket(bucket_name='03west-backup-databag',
                              key='s3bucket',
                              value='testing',
                              dry_run=True)
    print('end testing create_or_update_s3bucket', file=sys.stderr)
    print('------------------')
    print()
    print('testing get_s3nexus_artifacts without version')
    versions = get_s3nexus_artifacts(branch='galactus')
    dreambox.utils.print_structure(versions)
    print('------------------')
    # print('testing get_s3nexus_artifacts with version')
    # print(get_s3nexus_artifacts(branch='galactus', version='2.2'))
    # print('end testing get_s3nexus_artifacts')
    # print('------------------')
