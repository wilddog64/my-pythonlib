from __future__ import print_function
from collections import namedtuple
import dreambox.config.core as inifile

class Jenkins(object):

    def __init__(self, jenkins_config_file='', section=''):
        self._config = None
        if jenkins_config_file == '':
            self._jenkins_config_file = 'jenkins.ini'
        else:
            self._jenkins_config_file = jenkins_config_file
        self._section        = section
        self._name           = self._section
        self._config         = inifile.config_section_map(self._jenkins_config_file, section)
        self._user           = self._config['user']
        self._passwd         = self._config['password']
        self._url            = self._config['url']
        self._jobs           = None
        self._job            = namedtuple('Job', ['name', 'url', 'parameters'])
        self._job_parameters = namedtuple('Parameters', ['name', 'value'])

    @property
    def config_file(self):
        return self._jenkins_config_file

    @property
    def section(self):
        return self._section

    @property
    def user(self):
        return self._user

    @user.setter
    def user(self, value):
        self._user = value

    @property
    def passwd(self):
        return self._passwd

    @passwd.setter
    def passwd(self, value):
        self._passwd = value

    @property
    def url(self):
        return self._url

    @url.setter
    def url(self, value):
        self._url = value

    @property
    def server(self):
        return self._server.server

    @property
    def jobs(self):
        if self._jobs is None:
            self._jobs = {job['name']: (self._job(job['name'], job['url'], self._get_job_parameters(job['name'])))
                    for job in self._server.get_all_jobs()}
        return self._jobs

    @property
    def name(self):
        '''
        an alias for the self.section property
        '''
        return self._name
    
    def _get_job_info(self, job_name=''):
        return self._server.get_job_info(job_name)

    def _get_job_parameters(self, job_name=''):
        params = {}
        for p in self._get_job_info(job_name=job_name)['property'][0]['parameterDefinitions']:
            params['name'] = p['name']
            params['type'] = p['type']
            if 'defaultParameterValue' in p and 'value' in p['defaultParameterValue']:
                params[p['name']] = p['defaultParameterValue']['value']
            else:
                params[p['name']] = ''

        return params

if __name__ == '__main__':
    import dreambox.utils
    devops_jenkins = Jenkins('jenkins.ini', 'stage-devops-jenkins')
    print('jenkins configuration file: %s and section %s' % (devops_jenkins.config_file, devops_jenkins.section))
    print('jenkins server url: %s' % devops_jenkins.server)
    print('jenkins server user: %s' % devops_jenkins.user)
    # dreambox.utils.print_structure(devops_jenkins.jobs)
    if 'environment_create' in devops_jenkins.jobs:
        print('job url: %s' % devops_jenkins.jobs['build_terraform'].url)
        print('---- job info ---')
        build_terraform_info = devops_jenkins._get_job_info('build_terraform')
        dreambox.utils.print_structure(build_terraform_info)
        print('')
        dreambox.utils.print_structure(build_terraform_info['actions'][0]['parameterDefinitions'])
        print('')
        print('--- job parameters ---')
        dreambox.utils.print_structure(devops_jenkins._get_job_info('build_terraform'))
        print('')
        print('--- job info ---')
        dreambox.utils.print_structure(devops_jenkins.jobs['environment_create'])
        print('')
