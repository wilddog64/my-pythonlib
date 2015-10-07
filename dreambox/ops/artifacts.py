from __future__ import print_function
from distutils.version import LooseVersion
import re
import dreambox.aws.s3 as s3
import dreambox.utils

def list_s3nexus_versions(bucket='dreambox-deployment-files',
                          type='releases',
                          key='Nexus',
                          branch=None,):
   # construct an s3 path toward the valid s3 bucket
   path = 's3://%s/%s/%s/com/dreambox/dbl-%s-main/' % (bucket, key, type, branch)

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

if __name__ == '__main__':
    print('=== testing list_s3nexus_versions ===')
    versions = list_s3nexus_versions(branch='galactus')
    dreambox.utils.print_structure(versions)
    print('=== end testing list_s3nexus_versions without version ===')

