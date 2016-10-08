from __future__ import print_function
from dreambox.jenkins.core import Jenkins
import dreambox.utils

def jenkins():
    jenkins_config_filename = 'jenkins.ini'
    jenkins_config_filepath = '~/src/gitrepo/python/dreambox-pythonlib/dreambox/etc'
    jenkins_config_section  = 'stage-devops-jenkins'
    jobinfomap              = Jenkins.create_jobinfomap(Jenkins(jenkins_config_filename,
                                                                jenkins_config_filepath,
                                                                jenkins_config_section))
    environment_create = jobinfomap.environment_create
    dreambox.utils.print_structure(environment_create.job_info['property'][0]['parameterDefinitions'])

if __name__ == '__main__':
    jenkins()
