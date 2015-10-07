from __future__ import print_function
from distutils.version import LooseVersion
import re
import dreambox.aws.s3 as s3
import dreambox.utils
import sh

class S3NexusVersionError(sh.ErrorReturnCode):
    def __init__(self, message):
       super(sh.ErrorReturnCode, self).__init__(message)


class S3NexusBranchError(sh.ErrorReturnCode):
    def __init__(self, message):
       super(sh.ErrorReturnCode, self).__init__(message)


class S3NexusTypeError(sh.ErrorReturnCode):
    def __init__(self, message):
       super(sh.ErrorReturnCode, self).__init__(message)


class S3NexusInvalidPath(sh.ErrorReturnCode):
    def __init__(self, message):
       super(sh.ErrorReturnCode, self).__init__(message)


def get_s3nexus_versions(bucket='dreambox-deployment-files',
                          type='releases',
                          branch=None,):
    '''
get_s3nexus_versions is a function that return a list versions for a given branch.  The
function takes the following parameters,

* bucket is a valid s3 bucket
* type is a type of a build.  this can be either snapshots or releases
* branch is a product branch to look at
    '''

    if not type in ['snapshots', 'releases']:
       error = 'unsupprt type.  type can be either releases or snapshots, but [%s] is given' % type
       raise S3NexusTypeError(error)

    if branch is None:
       raise S3NexusBranchError('branch is a required parameter')

    # construct an s3 path toward the valid s3 bucket
    path = 's3://%s/Nexus/%s/com/dreambox/dbl-%s-main/' % (bucket, type, branch)

     # filter out all the noise strings and grab only version numbers to store in versions array
    output = None
    versions = []
    if path is not None:
       output = s3.ls(path)
       m = re.compile(r'\s+PRE\s|\/$')
       for line in output:
          if m.match(line):
             line = m.sub('', line).rstrip()
             versions.append(line)

    # return a sorted versions in descending order
    return sorted([LooseVersion(v).vstring for v in versions], reverse=True)


def get_s3nexus_artifacts(bucket='dreambox-deployment-files',
                          type='snapshots',
                          pkg='.zip',
                          branch=None,
                          version=None):
    '''
get_s3nexus_artifacts is a function that will return a list of nexus artifacts
that stores at AWS s3 bucket.  This function takes the folloiwng parameters,

* bucket an s3 bucket that stores nexus artifacts
* type can be either releases or snapshots
* pkg is a package type that this function is looking for.  by default, this is .zip
* branch is a build branch to look for. i.e. galactus, edex, ...
* version is a particular version for a given branch
    '''

    if not type in ['releases', 'snapshots']:
       error = 'unsupprt type.  type can be either releases or snapshots, but [%s] is given' % type
       raise S3NexusTypeError(error)

    if branch is None:
       raise S3NexusBranchError('branch is a required parameter')

    if version is None:
       raise S3NexusVersionError('version is a required parameter')

    if type == 'snapshots':
       version = "%s-SNAPSHOT" % version

    # s3 path
    path = 's3://%s/Nexus/%s/com/dreambox/dbl-%s-main/%s/' % (
          bucket,
          type,
          branch,
          version
          )

    # grab everything that ends with what specifies in pkg and stores
    # it in artifacts array
    artifacts = []
    try:
      lines = s3.ls(path)
    except sh.ErrorReturnCode_1:
       raise S3NexusInvalidPath('un-known s3 path: %s' % path)
    except sh.ErrorReturnCode:
       raise sh.ErrorReturnCode

    for line in lines:
       line = line.rstrip()
       if line.endswith(pkg):
          artifacts.append(line.split()[-1])

    # return a sorted versions in descending order
    return sorted([LooseVersion(v).vstring for v in artifacts], reverse=True)

if __name__ == '__main__':
    print('=== testing get_s3nexus_versions ===')
    versions = get_s3nexus_versions(branch='galactus')
    dreambox.utils.print_structure(versions)
    print('=== end testing get_s3nexus_versions without version ===')
    print()
    print('=== testing get_s3nexus_artifacts ===')
    print('get artifacts for snapshot build')
    artifacts = get_s3nexus_artifacts(branch='galactus', version='2.2')
    dreambox.utils.print_structure(artifacts)
    print('-------------------------------')
    print('get artifact for release build')
    artifacts = get_s3nexus_artifacts(type='snapshots', branch='galactusa', version='2.2')
    dreambox.utils.print_structure(artifacts)
    print('=== end testing get_s3nexus_artifact ===')
