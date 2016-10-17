from __future__ import print_function
from dreambox.jenkins.core import Jenkins
import argparse
import os
import datetime

def jenkins():
    '''
    is a function to construct a jenkins object, and build a proper 
    command line options. This function does not take any parameters.
    '''

    tmpdir      = os.path.join(os.curdir, 'tmp')
    pickle_file = os.path.join(tmpdir, 'obj.pickle')
    # find out where's jenkins configuration file,
    # jenkins.ini, and build a container object from it
    jenkins_config_filename = 'jenkins.ini'
    jenkins_config_filepath = '~/src/gitrepo/python/dreambox-pythonlib/dreambox/etc'
    jenkins_config_section  = 'stage-devops-jenkins'
    jobinfomap              = None
    if os.path.exists(pickle_file) and \
               Jenkins.timediff_in_secs(Jenkins.mdate(pickle_file),
                                        datetime.datetime.now()) > (5 * 60):
        print('pickle file expired, regenerating it')
        os.unlink(pickle_file)
    if not os.path.exists(pickle_file):
        jobinfomap = Jenkins.create_jobinfomap(Jenkins(jenkins_config_filename,
                                                       jenkins_config_filepath,
                                                       jenkins_config_section))
    else:
        print('no parent object pass in')
        jobinfomap = Jenkins.create_jobinfomap()
    # build command line options based on our container object, and activate it
    cmd_parser = build_cmdline_options(jobinfomap)
    args       = cmd_parser.parse_args()
    args.func(args)

def build_cmdline_options(jobinfos=None):
    '''
    is a function that builds out command line options.
    This function takes only one parameter,

    * jobinfos is a type of JobInfos
    '''
    # create a command line parser object
    optionparser = argparse.ArgumentParser(prog='jenkins',
                                           description='jenkins jobs')

    # create sub parser objects and declare some variables
    subparsers  = optionparser.add_subparsers()
    opt_name    = ''
    opt_default = ''
    opt_help    = ''
    opt_choices = None

    # now iterates through a jobinfos container
    for jobinfo in jobinfos:
        subparser = subparsers.add_parser(jobinfo) # create a parser for subcommand

        # get job parameters and iterate through them to build subcommand options
        params = jobinfos[jobinfo].parameters
        for param in params:
            opt_type = params[param].type
            if not 'Separator' in opt_type:
                opt_name    = '--%s' % param
                opt_default = params[param].default
                opt_help    = params[param].description
                opt_choices = params[param].value if 'Choice' in opt_type else None
                if opt_choices:
                    if 'Required' in opt_default:
                        subparser.add_argument(opt_name, choices=opt_choices, required=True)
                    else:
                        subparser.add_argument(opt_name, choices=opt_choices)
                else:
                    subparser.add_argument(opt_name, help=opt_help, default=opt_default)
                subparser.set_defaults(func=jobinfos[jobinfo].build)

    return optionparser


if __name__ == '__main__':
    jenkins()
