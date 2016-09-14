from __future__ import print_function
import jenkins
import dreambox.config.core as inifile

class Jenkins(object):

    def __init__(self, jenkins_config_file='', section=''):
        self._config = None
        if jenkins_config_file == '':
            jenkins_config_file = 'jenkins.ini'
        self._config = inifile.config_section_map(jenkins_config_file, section)
        self._user    = self._config['user']
        self._passwd  = self._config['password']
        self._url     = self._config['url']
        self._jobs    = None
        self._server = jenkins.Jenkins(self._url, self._user, self._passwd)

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
            self._jobs = {job['fullname']: job['url'] 
                    for job in self._server.get_all_jobs()}
        return self._jobs
    
    def job_info(self, job_name=''):
        return self._server.get_job_info(job_name)

if __name__ == '__main__':
    import dreambox.utils
    devops_jenkins = Jenkins('jenkins.ini', 'stage-devops-jenkins')
    print('jenkins server url: %s' % devops_jenkins.server)
    print('jenkins server user: %s' % devops_jenkins.user)
    dreambox.utils.print_structure(devops_jenkins.jobs)
    if 'build_terraform' in devops_jenkins.jobs:
        print('job url: %s' % devops_jenkins.jobs['build_terraform'])
        dreambox.utils.print_structure(devops_jenkins.job_info('build_terraform'))
