import boto3
import re

class Aws(object):
    '''
    Aws is a base class for all other classes regarding to Amazon Web
    Service functions. This class wraps boto3 library to provide functionality
    to work in AWS platform.
    '''
    def __init__(self, aws_client=None, region=None):
        '''
        The constructor that initializes access to various AWS service. After
        a service is initialized, a couple of private members are created for
        used by a subclass. The constructor takes one parameter,

        * region - a valid region defined by AWS. By default, this is none, and
                   the object will use your awscli configuration store at ~/.aws/config
                   file

        '''
        self._aws          = boto3.client(aws_client, region)
        self._paginator    = self._aws.get_paginator
        self._waiter       = self._aws.get_waiter
        self._can_paginate = self._aws.can_paginate
        self._meta         = self._aws.meta
        self._resource     = boto3.resource

    def region_name(self):
        return self._meta.config.region_name

    def paginator(self, ops=None):
        '''
        Create a paginator object. This method takes one parameter,

        * ops which is a valid boto3 method initialized by the boto3.client
        '''
        if self._can_paginate(ops):
            return self._paginator(ops)
        else:
            return None

    def resource(self, resource_name=None):
        '''
        return boto3 resource object back to caller.

        * resource_name is a valid resource defined by boto3
        '''
        return self._resource(resource_name, self.region_name())

    @staticmethod
    def convert_case(name=None):
        '''
        is a utility method that turns camel case into python convention,
        i.e. CamelCase -to camel_case
        '''
        s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
        return re.sub('([a-z0-9])(A-Z)', r'\1_\2', s1).lower()

class Tag(object):
    '''
    a class to store AWS tag
    '''

    def __setattr__(self, name, value):
        '''
        automatically create an accessor methods here. The method store key, value
        pair in internal __dict__ object. This method also convert camel case into
        python case convention.
        '''
        self.__dict__[name] = value


