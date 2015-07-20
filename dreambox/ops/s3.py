from __future__ import print_function

from funcy.colls import select
import dreambox.utils
import sys

from dreambox.aws.core import aws_s3api_cmd

def get_buckets(profile=None,
                region=None,
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

    s3_buckets = aws_s3api_cmd(aws_profile=profile,
                               aws_region=region,
                               s3api_subcmd='list-buckets',
                               dry_run=dry_run,
                               verbose=verbose)
    return_rst = s3_buckets['Buckets']
    if filterby is not None:
       return_rst = select(lambda bucket: filterby.lower() in bucket['Name'],
                           return_rst)
    return return_rst


if __name__ == '__main__':

    print('testing get_bucket', file=sys.stderr)
    print('------------------')
    buckets = get_buckets(filterby='backup-databag')
    dreambox.utils.print_structure(buckets)
    print('end testing get_bucket', file=sys.stderr)
    print('------------------')
