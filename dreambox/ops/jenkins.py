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

    global jobinfomap
    tmpdir      = os.path.join(os.curdir, 'tmp')
    pickle_file = os.path.join(tmpdir, 'obj.pickle')
    # find out where's jenkins configuration file,
    # jenkins.ini, and build a container object from it
    jenkins_config_filename = 'jenkins.ini'
    jenkins_config_filepath = '~/src/gitrepo/python/dreambox-pythonlib/dreambox/etc'
    jenkins_config_section  = 'stage-devops-jenkins'
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
                                           description='jenkins jobs',
                                           add_help=False)


    # create sub parser objects and declare some variables
    subparsers  = optionparser.add_subparsers()
    opt_name    = ''
    opt_default = ''
    opt_help    = ''
    opt_choices = None

    # now iterates through a jobinfos container
    for jobinfo in jobinfos:
        subparser = subparsers.add_parser(jobinfo, parents=[optionparser]) # create a parser for subcommand

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

    # setup command line options for copy-job
    subparser = subparsers.add_parser('copy-job')
    subparser.add_argument('--job-name',
                           required=True,
                           help='create a copy of current jenkins job',
                           dest='jobname')
    subparser.add_argument('new_name')
    subparser.set_defaults(func=copy_job)

    # setup command line option for delete-job
    subparser = subparsers.add_parser('delete-job')
    subparser.add_argument('job_name', help='delete a jenkins job')
    subparser.set_defaults(func=delete_job)

    # setup command line option for enable-job
    subparser = subparsers.add_parser('enable-job')
    subparser.add_argument('job_name', help='enable a jenkin job')
    subparser.set_defaults(func=enable_job)

    # setup command line option for disable-job
    subparser = subparsers.add_parser('disable-job')
    subparser.add_argument('job_name', help='disable a jenkins job')
    subparser.set_defaults(func=disable_job)

    return optionparser

def __get_object_method(jobinfomap, jobname, method):
    meth = None
    if jobname in jobinfomap:
        meth = getattr(jobinfomap[jobname], method)
    else:
        raise IndexError('unable to find jenkins job %s' % jobname)

    return meth

def copy_job(args):
    '''
    create a copy of a given jenkins job
    '''
    jobname   = args.jobname
    new_name  = args.new_name
    func      = __get_object_method(jobinfomap, jobname, 'copy')
    func(new_name)

def delete_job(args):
    jobname  = args.job_name
    func     = __get_object_method(jobinfomap, jobname, 'delete')
    func()

def enable_job(args):
    jobname  = args.job_name
    func     = __get_object_method(jobinfomap, jobname, 'enable')
    func()


def disable_job(args):
    jobname  = args.job_name
    func     = __get_object_method(jobinfomap, jobname, 'disable')
    func(args)

if __name__ == '__main__':
    jenkins()
