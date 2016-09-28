from __future__ import print_function
from collections import namedtuple
import dreambox.config.core as inifile
import jenkins
from xmljson import BadgerFish
from xml.etree.ElementTree import fromstring
import json

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
        self._server         = jenkins.Jenkins(self.url, self.user, self._passwd)
        self._job            = namedtuple('Job', ['name', 'url', 'parameters'])
        self._job_parameters = namedtuple('Parameters', ['name', 'value'])
        self._bf             = BadgerFish()

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

    def _get_jobs(self):
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
    
    def _get_job_parameters(self, job_name=''):
        params = {}
        for p in self._server.get_job_info(job_name)['property'][0]['parameterDefinitions']:
            params['name'] = p['name']
            if 'defaultParameterValue' in p and 'value' in p['defaultParameterValue']:
                params[p['name']] = p['defaultParameterValue']['value']
            else:
                params[p['name']] = ''

        return params

    def _load_xml(self, xmlstring=''):
       return json.loads(json.dumps(self._bf.data(fromstring(xmlstring))))

    @classmethod
    def create_jobinfos(self, object):
        '''
        is a static method that create a JobInfos collection. This
        method takes one parameter

        object is an object of type dreambox.jenkins.core.Jenkins
        '''
        if type(object) is not dreambox.jenkins.core.Jenkins:
            raise TypeError('%s is not a type of core.Jenkins' % object.__class__)

        jobinfos = dreambox.jenkins.JobInfo.JobInfos()
        for job in object._get_jobs():
            jobinfo             = dreambox.jenkins.JobInfo.JobInfo(object)
            jobinfo._name       = job
            jobinfo._url        = object._get_jobs()[job].url
            parameters          = object._get_jobs()[job].parameters
            jobinfo._parameters = parameters
            jobinfos           += jobinfo

        return jobinfos

    @classmethod
    def create_jobinfomap(self, object):
        '''
        will create a JobInfoMap container object. The method takes one parameter

        * object which is a type of JobInfo
        '''
        if type(object) is not dreambox.jenkins.core.Jenkins:
            raise TypeError('%s is not a type of core.Jenkins' % object.__class__)
        jobinfomap = dreambox.jenkins.JobInfo.JobInfoMap()
        for job in object._get_jobs():
            jobinfo             = dreambox.jenkins.JobInfo.JobInfo(object)
            jobinfo._name       = job
            jobinfo._url        = object._get_jobs()[job].url
            parameters          = object._get_jobs()[job].parameters
            jobinfo._parameters = parameters
            setattr(jobinfomap, jobinfo.name, jobinfo)

        return jobinfomap

if __name__ == '__main__':
    import dreambox.jenkins
    import dreambox.jenkins.JobInfo
    import dreambox.utils
    devops_jenkins = dreambox.jenkins.core.Jenkins('jenkins.ini', 'stage-devops-jenkins')
    print('object type for devops_jenkins is %s' % type(devops_jenkins))
    print('jenkins configuration file: %s and section %s' % (devops_jenkins.config_file, devops_jenkins.section))
    print('jenkins server url: %s' % devops_jenkins.server)
    print('jenkins server user: %s' % devops_jenkins.user)
    print('--- testing Jenkins.create_jobinfos class method ---')
    jobinfos = Jenkins.create_jobinfos(devops_jenkins)
    jobs = [job for job in jobinfos if job.name == 'environment_create']
    for job in jobs:
        print('job name %s' % job.name)
        dreambox.utils.print_structure(job.parameters)
    print('--- testing Jenkins.create_jobinfos class method ---')
    print('')
    print('--- testing Jenkins.create_jobinfomap class method ---')
    jobinfomap = Jenkins.create_jobinfomap(devops_jenkins)
    print('a list of job:')
    print('-------------')
    for job in jobinfomap:
        print(job)
    print('-------------')
    print('')
    print('environment_create job config')
    dreambox.utils.print_structure(jobinfomap['environment_create'].get_job_config())
    print('')
    print('environment_create job info')
    dreambox.utils.print_structure(jobinfomap['environment_create'].get_job_info())
    print('--- testing Jenkins.create_jobinfomap class method ---')
