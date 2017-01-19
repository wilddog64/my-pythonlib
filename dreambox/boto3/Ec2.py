from Aws import Aws

class EC2(Aws):
    '''
    A class that provide an EC2 operations
    '''

    def __init__(self, region=None, instance_ids=None):
        '''
        A constructor to intialize an Autoscaling object. The constructor takes
        these parameters,

        * region is a valid AWS region. If it is None (default value), read from
          ~/.aws/config

        * instance_id is a list of ec2 instance ids
        '''
        # initialize object as an ec2 object
        super(self.__class__, self).__init__(aws_client='ec2', region=region)
        self._instance_ids = []
        if instance_ids and type(instance_ids) is list:
            self._instance_ids = instance_ids

        self._ec2_resource = self.resource(resource_name='ec2')

    def instances(self):
        '''
        return boto3.ec2.Instances object for a given list of instance ids
        '''
        # create a list of ec2.Instance objects and return them as a list
        instances = self._ec2_resource.instances.filter(InstanceIds=self._instance_ids)
        return list(instances)


if __name__ == '__main__':
    import utils
    # instaniate ec2 object with these instance ids
    ec2 = EC2(region='us-west-2', instance_ids=['i-f534f85a'])
    print('=== testing EC2 object with AWS region %s ===' % ec2.region_name())
    print('--- testing ec2.instances method ---')
    # obtains a list of ec2.Instance objects
    instances = ec2.instances()
    utils.print_structure(instances)
    # iterate through each object and print out its private
    # dns name and instance id
    for instance in instances:
        print('private DNS name: %s for %s' % 
                (instance.private_dns_name, instance.id))
    print('--- end testing ec2.instances method ---')
    print('=== end testing EC2 object with AWS region %s ===' % ec2.region_name())
