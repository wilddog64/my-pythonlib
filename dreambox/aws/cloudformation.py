from __future__ import print_function
import dreambox.aws.core as aws
from funcy.colls import select
import dreambox.utils
import re
import sys


def get_stack_names_from_all_regions(profile='',
                                     regions=None,
                                     qry='Stacks[].StackName'):
    '''
get_stack_names_from_all_regions will return all stacks from known

AWS regions (by default these regions are us-east-1 and us-west-2).  The
function accepts 3 parameters,

  profile: a profile define in ~/.aws/config
  regions: a list of AWS region that this function will retrieve stack names
  qry: a json query string

get_stack_names_from_all_regions will only return name with stageN (n is a
number from 1 - 9)
    '''
    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    region_stacks = {}
    m = re.compile(r'^stage\d$', re.IGNORECASE)
    for region in regions:
        region_stack = [r for r in aws.cloudformation('describe-stacks',
                                                      profile=profile,
                                                      region=region,
                                                      query=qry)
                        if m.match(r)]
        region_stacks[region] = region_stack

    return region_stacks


def get_all_stacks_for_stage(profile='',
                             region=None,
                             filterby=None):
    '''
get_all_stacks_for_stage will return all the stacks exists for a given stage
environment.  It takes the following parameters,

profile - aws profile if one exist.  If it is not provided, the function will
          try to use IAM profile if a given instance has one.
region - which aws region do we want to work on
filterby - limit result by providing a filter string
    '''
    stage_stacks = aws.cloudformation('describe-stacks',
                                      profile=profile,
                                      region=region,
                                      query='Stacks[].StackName')

    stacks_list = None
    if stage_stacks:
      stacks_list = select(lambda x: filterby.lower() in x.lower(), stage_stacks)
    return stacks_list


def get_stack_events(profile=None, region=None, stack_name=None):
    '''
get_stack_events return all the events for a given stack.  This function
takes the following parameters,

profile is an aws profile if one is provide; otherwise looking for default
profile in ~/.aws/config or IAM profile for a node

region is an AWS region that this function will work on

stack_name is a name of stack that contains the event this function is looking
for
    '''
    stack_events = aws.cloudformation('describe-stack-events',
                                      profile=profile,
                                      region=region,
                                      stack_name=stack_name,
                                      query='StackEvents[]')
    return stack_events


def get_all_stackevents_for_stage(profile='', region=None, filterby=None):
    '''
get_all_stackevents_for_stage will collect all cloudformation stack events for a
given stage environment.  The function takes the following parameters,

profile is an aws profile if one is provide; otherwise looking for default
profile in ~/.aws/config or IAM profile for a node

region is an AWS region that this function will work on

filterby is a stage environment name, i.e. stage1 ... stage9
    '''

    stack_names = get_all_stacks_for_stage(profile=profile,
                                           region=region,
                                           filterby=filterby)
    stacks_events = {}
    for stack_name in stack_names:
        stacks_events['stack_name'] = get_stack_events(profile=profile,
                                                       region=region,
                                                       stack_name=stack_name)


def get_cloudformation_stack_info(profile='', regions=None, environ=None, dry_run=False):
    '''
get_cloudformation_stack_info will return cloudformation stack information for a
given environemnt.  This function takes the following parameters,


profile is an aws profile if one is provide; otherwise looking for default
profile in ~/.aws/config or IAM profile for a node

region is an AWS region that this function will work on

environ is a stage environment name, i.e. stage1 ... stage9
    '''
    if regions is None:
        regions = ['us-east-1', 'us-west-2']

    def create_cloudformation_stack_objects(stack_list, environ=None):
        stack_objects = stack_list
        if (environ and stack_list) is not None:
            stack_objects = select(lambda x: environ.lower() == x[0].lower(),
                                   stack_list)

        stack_table = {}
        if stack_objects:
            for stack_object in stack_objects:
               stack_name = stack_object[0].lower()
               stack_table[stack_name] = {}
               for parameters in stack_object[1]:
                   dreambox.utils.print_structure(parameters)
                   stack_table[stack_name][parameters['ParameterKey']] = parameters['ParameterValue']

        return stack_table

    stack_infos = {}
    for region in regions:
        stack_info = aws.cloudformation('describe-stacks',
                                        profile=profile,
                                        region=region,
                                        dry_run=False,
                                        query='Stacks[].[StackName,Parameters[]]')
        if region:
            stack_infos[region] = create_cloudformation_stack_objects(stack_info,
                                                                      environ)

    return stack_infos


def create_stack(profile='',
                 region=None,
                 dry_run=False,
                 verbose=False,
                 **stack_options):
    '''
create_stack will creates a cloudformation stack via aws cloudformation
create-stack command.  This function takes the following parameters,

* profile is an aws profile if one is provide; otherwise looking for default
  profile in ~/.aws/config or IAM profile for a node
* region is an AWS region that this function will work on
* stack_options is a python special **args options, which is a dictionary object
  that contains key and value pair.  This special options have to be acceptible
  by aws cloudformation create-stacks.  Refers to document for what are the
  valid options.

The function return stackId upon success
    '''

    stack_id = aws.cloudformation('create-stack',
                                  profile=profile,
                                  region=region,
                                  dry_run=dry_run,
                                  verbose=verbose,
                                  **stack_options)

    return stack_id


if __name__ == '__main__':
    stacks = get_all_stacks_for_stage(region='us-west-2', filterby='stage3')
    dreambox.utils.print_structure(stacks)

    print('testing get_all_stackevents_for_stage stage3')
    stage_stack_events = get_all_stackevents_for_stage(region='us-west-2',
                                                       filterby='stage3')
    dreambox.utils.print_structure(stage_stack_events)
    print('end testing get_all_stackevents_for_stage stage3')

    print('testing get_cloudformation_stack_info')
    stacks = get_cloudformation_stack_info(environ='stage3')
    dreambox.utils.print_structure(stacks)
    print('end testing get_cloudformation_stack_info')

    print('testing create_stack', file=sys.stderr)
    stack_id = create_stack(region='us-west-2',
                            dry_run=True,
                            stack_name='stage4',
                            template_url='https://s3.amazonaws.com/cfnwest/stage3',
                            parameters='ParameterKey=stage4,ParameterValue=testing',
                            capabilities='CAPABILTY_IAM')
