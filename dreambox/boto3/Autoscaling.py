from __future__ import print_function
import boto3
import dreambox.utils
from Aws import Aws
from Aws import Tag

class Autoscaling(Aws):
    def __init__(self, region=None, stack=None):
        '''
        A constructor to intialize an Autoscaling object. The constructor takes
        one parameter, 
        
        * region, which is a valid region define by AWS
        * stack is an stack to look for

        '''
        super(self.__class__, self).__init__(aws_client='autoscaling', region=region)
        self._stack = stack

    def __setattr__(self, name, value):
        '''
        automatically create an accessor methods here. The method store key, value
        pair in internal __dict__ object. This method also convert camel case into
        python case convention.
        '''
        name = Aws.convert_case(name)
        self.__dict__[name] = value

    def name(self):
        '''
        return the name of the autoscaling object
        '''
        return self.name

    def _get_all_autoscaling_groups(self, filter_by=None):
        '''
        will return a hash contains all autoscaling group 
        from a given AWS region, the hash it returns contains:

            {
                'AutoScalingGroupName': [
                    'instances': Instances,
                    'tags': Tags
                ]
            }

        The method takes one parameter,

        * filter_by is a stack to look for

        Note: Instances and Tags are part of the hash and list from
        the result of describe_auto_scaling_groups method call.
        '''

        # set filter_by to _stack if it is None and _stack is set
        if filter_by is None and self._stack is not None:
            filter_by = self._stack

        # iterates through each page and construct a list of hash tables
        # we use AutoScalingGroupName as a key, and store Instances and Tags object in its
        # own keys respectively: instances and tags
        autoscaling_groups = []
        for asg in self.paginator('describe_auto_scaling_groups').paginate():
            autoscaling_group_infos = [{asg['AutoScalingGroupName']: {
                    'instances': asg['Instances'],
                    'tags': asg['Tags']}}
                for asg in asg['AutoScalingGroups']]
            autoscaling_groups += autoscaling_group_infos

        # if filter_by is not None, then we iterate through a list and
        # get the autoscaling group we are looking for
        if filter_by:
            asgs = []
            for autoscaling_group in autoscaling_groups:
                for key, item in autoscaling_group.items():
                    if filter_by.lower() in key.lower():
                        asgs.append({ key: item })
            autoscaling_groups = asgs

        return autoscaling_groups

    def _get_all_autoscaling_groups_for(self, stack=None):
        '''
        will return all the autoscaling group for a given stack.

        * stack is a chef stack

        The method call get_all_autoscaling_groups and pass stack to filter_by
        parameter.
        '''
        if stack is None:
            stack = self._stack

        return self._get_all_autoscaling_groups(filter_by=stack)

    def _get_instance_ids_for(self, stack=None):
        ''' 
        return all the instance ids for a given stack.

        * stack is a chef stack
        '''
        if stack is None:
            stack = self._stack

        # first we retrieve all autoscaling groups for a given stack
        autoscaling_groups = self._get_all_autoscaling_groups_for(stack=stack)

        # now we extract InstanceId from each autoscaling group
        instance_ids_list = []
        for autoscaling_group in autoscaling_groups:
            for asg_name, asg in autoscaling_group.items():
                instances = asg['instances']
                instance_ids_list += [instance['InstanceId'] for instance in instances]

        return instance_ids_list

    def create_resources(self, stack=None):
        '''
        return a list of autoscaling objects. This method takes one parameter,

        * stack is a chef stack. If it is None (by default), it
          gets a value set by constructor
        '''
        autoscaling_list = []
        autoscaling_groups = self._get_all_autoscaling_groups(filter_by=stack)
        for autoscaling_group in autoscaling_groups:
            for asg_name, asg in autoscaling_group.items():
                autoscaling_obj            = Autoscaling()
                autoscaling_obj.name       = asg_name
                autoscaling_obj.instances  = Autoscaling._handle_instances(obj=autoscaling_obj, instances=asg['instances'])
                autoscaling_obj.tags       = Autoscaling._handle_tags(obj=autoscaling_obj, tags=asg['tags'])
            autoscaling_list.append(autoscaling_obj)

        return autoscaling_list

    def suspend_processes(self):
        '''
        suspend autoscaling processes
        '''
        self._aws.suspend_process(AutoScalingGroupName=self.name())

    def resume_processes(self):
        '''
        resume autoscaling processes
        '''
        self._aws.resume_process(AutoScalingGroupName=self.name())

    def create_or_update_tags(self, key=None, tags=None):
        '''
        this method will create or update tags for a given auto scaling group.
        The method accepts one paramter,

        * tags are a list of hash like this,

          [
            {
                'ResourceId': 'name of the autoscaling group',
                'ResourcceType': 'auto-scaling-group',
                'Key': 'your_key',
                'Value': 'value for the key',
                'PropagateAtLaunch': 'true|false',
            }
          ]
        '''
        self._aws.create_or_update_tags(Tags=tags)

    @staticmethod
    def _handle_instances(obj=None, instances=None):
        from Ec2 import EC2
        instances_list = []
        for instance in instances:
            ec2 = EC2(instance_ids=[instance['InstanceId']])
            obj.launch_configuration_name = instance['LaunchConfigurationName']
            instances_list.append(ec2)
        return instances_list

    @staticmethod
    def _handle_tags(obj=None, tags=None):
        tag_list = []
        t = Tag()
        for tag in tags:
            for key, value in tag.items():
                setattr(t, key, value)
        tag_list.append(t)

        return tag_list

if __name__ == '__main__':
    print('initialize autoscaling object')
    autoscaling = Autoscaling()
    print('=== get all autoscaling groups from AWS %s ===' % autoscaling.region_name())
    dreambox.utils.print_structure(autoscaling._get_all_autoscaling_groups())
    print('')
    print('--- filter autoscaling group, looking for stage7 ---')
    print('')
    dreambox.utils.print_structure(autoscaling._get_all_autoscaling_groups(filter_by='stage7'))
    print('')
    print('=== end get all autoscaling groups from AWS %s ===' % autoscaling.region_name())
    print('')
    print('=== get all autoscaling groups for a given stack from AWS %s ===' % autoscaling.region_name())
    dreambox.utils.print_structure(autoscaling._get_all_autoscaling_groups_for(stack='stage7-play'))
    print('=== end get all autoscaling groups for a given stack from AWS %s ===' % autoscaling.region_name())
    print('')
    print('=== get all instance ids from autoscaling groups for a given stack from AWS %s ===' % autoscaling.region_name())
    dreambox.utils.print_structure(autoscaling._get_instance_ids_for(stack='stage7-play'))
    print('')
    print('=== now testing constructor with stack is set ===')
    autoscaling = Autoscaling(stack='stage7-play')
    print('--- initialize autoscaling object with stack set to stage7-play from AWS %s ---' % autoscaling.region_name())
    dreambox.utils.print_structure(autoscaling._get_all_autoscaling_groups())
    print('=== end testing constructor with stack is set ===')
    print('')
    print('=== testing autoscaling.create_resource methods ===')
    print('--- testing create_resources without parameter (set stack from constructor) ---')
    autoscaling = Autoscaling(stack='stage7-play')
    autoscaling_groups = autoscaling.create_resources()
    for autoscaling_group in autoscaling_groups:
        print('autoscaling group name: %s' % autoscaling_group.name)
        for tag in autoscaling_group.tags:
            print('PropagateAtLaunch is %s' % tag.PropagateAtLaunch)

    print('--- end testing create_resources without parameter (set stack from constructor) ---')
    
    print('=== end testing autoscaling.create_resource methods ===')
