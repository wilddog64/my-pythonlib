from __future__ import print_function
from dreambox.jenkins.core import Jenkins
import argparse

def jenkins():
    '''
    is a function to construct a jenkins object, and build a proper command line options
    This function does not take any parameters.
    '''

    # find out where's jenkins configuration file, jenkins.ini, and build a container
    # object from it
    jenkins_config_filename = 'jenkins.ini'
    jenkins_config_filepath = '~/src/gitrepo/python/dreambox-pythonlib/dreambox/etc'
    jenkins_config_section  = 'stage-devops-jenkins'
    jobinfomap              = Jenkins.create_jobinfomap(Jenkins(jenkins_config_filename,
                                                                jenkins_config_filepath,
                                                                jenkins_config_section))
    # build command line options based on our container object, and activate it
    cmd_parser = build_cmdline_options(jobinfomap)
    cmd_parser.parse_args()

def build_cmdline_options(jobinfos=None):
    optionparser = argparse.ArgumentParser(prog='jenkins',
                                           description='jenkins jobs')
    subparsers    = optionparser.add_subparsers()
    opt_name     = ''
    opt_default  = ''
    opt_help     = ''
    opt_choinces = None
    for jobinfo in jobinfos:
        subparser = subparsers.add_parser(jobinfo)
        job_parameters = jobinfos[jobinfo].job_info['property'][0]['parameterDefinitions']
        for job_parameter in job_parameters:
            opt_type = job_parameter['type']
            if not 'Separator' in opt_type:
                opt_name     = '--%s' % job_parameter['name']
                opt_default  = job_parameter['defaultParameterValue']['value'] if job_parameter['defaultParameterValue']['value'] else ''
                opt_help     = job_parameter['description']
                opt_choinces = job_parameter['choices'] if 'Choice' in opt_type else None
                if opt_choinces:
                    subparser.add_argument(opt_name, choices=opt_choinces)
                else:
                    subparser.add_argument(opt_name, help=opt_help, default=opt_default)
                subparser.set_defaults(func=jobinfos[jobinfo].build)

    return optionparser


if __name__ == '__main__':
    jenkins()
