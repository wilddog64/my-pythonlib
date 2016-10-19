from __future__ import print_function
from dreambox.jenkins.core import Jenkins
import argparse, argcomplete

def jenkins():
    '''
    is a main entry function to construct a jenkins object,
    and build a proper command line options.
    This function does not take any parameters.
    '''

    # create a command line parser object
    optionparser = argparse.ArgumentParser(prog='jenkins',
                                           description='jenkins jobs')

    # setup argcomplete
    argcomplete.autocomplete(optionparser)

    # mark jobinfomap global makes command line function hook much more easy
    # to access JobInfoMap object
    global jobinfomap

    # find out where's jenkins configuration file,
    # jenkins.ini, and build a container object from it
    jenkins_config_filename = 'jenkins.ini'
    jenkins_config_filepath = '~/src/gitrepo/python/dreambox-pythonlib/dreambox/etc'
    jenkins_config_section  = 'stage-devops-jenkins'

    optionparser.add_argument('--config-path', '-c',
                              help='a full path to the jenkins configuration file',
                              default=jenkins_config_filepath)
    optionparser.add_argument('--config-filename', '-n',
                              help='a base name of the configuration file',
                              default=jenkins_config_filename)
    optionparser.add_argument('--jenkins-config-section', '-j',
                              help='a section name define in jenkins configuration file',
                              default=jenkins_config_section)
    optionparser.add_argument('--cache-timeout', '-t',
                              help='pickle file timeout in minutes',
                              default=5)
    optionparser.add_argument('--user', '-u',
                              help='a user that can connect to jenkins server')
    optionparser.add_argument('--password', '-p',
                              help='a password assoicate with jenkins user')

    # create object and cache it if the pickle file does not exist
    global jenkins
    jenkins = Jenkins(jenkins_config_filename,
                      jenkins_config_filepath,
                      jenkins_config_section)
    jobinfomap = Jenkins.create_jobinfomap(jenkins)

    # build command line options based on our container object, and activate it
    cmd_parser = build_cmdline_options(optionparser, jobinfomap)
    args       = cmd_parser.parse_args()
    args.func(args)

def build_cmdline_options(optionparser, jobinfos=None):
    '''
    is a function that builds out jenkins command and command
    line options base on what's available from jenkins server.
    This function takes only one parameter,

    * jobinfos is a type of JobInfos
    '''
    # create sub parser objects and declare some variables
    subparsers  = optionparser.add_subparsers()
    opt_name    = ''
    opt_default = ''
    opt_help    = ''
    opt_choices = None

    # now iterates through a jobinfos container
    for jobinfo in jobinfos:
        # create a parser for subcommand
        subparser = subparsers.add_parser(jobinfo, help=jobinfo.replace('_', ' '))

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
    subparser = subparsers.add_parser('copy-job', help='copy current jenkins job as a different name')
    subparser.add_argument('--job-name',
                           required=True,
                           help='existing jenkins job name',
                           dest='jobname')
    subparser.add_argument('new_name', help='new job name')
    subparser.set_defaults(func=copy_job)

    # setup command line option for delete-job
    subparser = subparsers.add_parser('delete-job', help='delete a jenkins job')
    subparser.add_argument('job_name', help='jenkins job to be deleted')
    subparser.set_defaults(func=delete_job)

    # setup command line option for enable-job
    subparser = subparsers.add_parser('enable-job', help='enable a jenkins job')
    subparser.add_argument('job_name', help='jenkins job to be enable')
    subparser.set_defaults(func=enable_job)

    # setup command line option for disable-job
    subparser = subparsers.add_parser('disable-job', help='disable a jenkins job')
    subparser.add_argument('job_name', help='jenkins job to be disable')
    subparser.set_defaults(func=disable_job)

    # setup command line option for list-jobs
    subparser = subparsers.add_parser('list-all-jobs', help='list all jenkins jobs')
    subparser.set_defaults(func=list_all_jobs)

    # setup command line option for list-disable-jobs
    subparser = subparsers.add_parser('list-disable-jobs', help='list all jenkins jobs that are disable')
    subparser.set_defaults(func=list_disable_jobs)

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

def list_all_jobs(args):
    print('----')
    for job in jenkins._server.get_all_jobs():
        print(job['fullname'])

def list_disable_jobs(args):
    print('---')
    for job in jenkins._server.get_all_jobs():
        jobname = job['fullname']
        if not 'parameterDefinitions' in jenkins._server.get_job_info(jobname)['property'][0]:
            print(jobname)

if __name__ == '__main__':
    jenkins()
