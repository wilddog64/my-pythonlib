from __future__ import print_function
import dreambox.config.core as inifile
import jenkins
from xmljson import BadgerFish
from xml.etree.ElementTree import fromstring
import json
import dreambox.jenkins
import dreambox.jenkins.JobInfo

import os
import datetime
import tempfile

# if cPickle is available the include it; otherwise
# use pure Python implementation
try:
    import cPickle as pickle
except:
    import pickle

class Jenkins(object):

    def __init__(self, config_file='', config_file_path='', section=''):
        self._config = None
        if config_file == '':
            self._jenkins_config_file = 'jenkins.ini'
        else:
            self._jenkins_config_file = config_file
        self._section        = section
        self._name           = self._section
        self._config         = inifile.config_section_map(self._jenkins_config_file,
                                                          config_file_path,
                                                          section)
        self._user           = self._config['user']
        self._passwd         = self._config['password']
        self._url            = self._config['url']
        self._jobs           = None
        self._server         = jenkins.Jenkins(self.url, self.user, self._passwd)
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
            self._jobs = {job['name']: dreambox.jenkins.JobInfo.Job(job['name'],
                                                                    job['url'],
                                                                    self._get_job_parameters(job['name']))
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
        parameter_definitions = self._server.get_job_info(job_name)['property'][0]['parameterDefinitions']
        for p in parameter_definitions:
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
        def _create_jobinfomap():
            jobinfomap = dreambox.jenkins.JobInfo.JobInfoMap()
            for job in object._get_jobs():
                jobinfo             = dreambox.jenkins.JobInfo.JobInfo(object)
                jobinfo._name       = job
                jobinfo._url        = object._get_jobs()[job].url
                parameters          = object._get_jobs()[job].parameters
                jobinfo._parameters = parameters
                setattr(jobinfomap, jobinfo.name, jobinfo)
            return jobinfomap

        current_dir = os.path.curdir
        workspace = os.path.join(current_dir, 'tmp')
        if not os.path.exists(workspace):
            os.mkdir(workspace)
        pickle_file = os.path.join(workspace, 'obj.pickle')
        pickle_filehandle = None
        load_from_pickle = False
        jobinfomap = None
        pickle_filehandle = None
        try:
            if not os.path.exists(pickle_file):
                pickle_filehandle = open(pickle_file, 'w+b')
            elif os.path.exists(pickle_file) and \
                Jenkins.timediff_in_secs(Jenkins.mdate(pickle_file), datetime.datetime.now()) > (5 * 60):
                os.unlink(pickle_file)
                pickle_filehandle = open(pickle_file, 'w+b')
            else:
                pickle_filehandle = open(pickle_file, 'r+b')
                load_from_pickle = True

            if type(object) is not dreambox.jenkins.core.Jenkins:
                raise TypeError('%s is not a type of core.Jenkins' % object.__class__)

            jobinfomap = None
            if load_from_pickle:
                print('reloading object')
                jobinfomap = pickle.load(pickle_filehandle)
                jobinfomap.establish_object_connections(object)
            else:
                jobinfomap = _create_jobinfomap()
                pickle.dump(jobinfomap, pickle_filehandle)
        finally:
            pickle_filehandle.close()


        return jobinfomap

    @staticmethod
    def mdate(filename):
        mtime = os.path.getmtime(filename)
        return datetime.datetime.fromtimestamp(mtime)
                                                      
    @staticmethod
    def timediff_in_secs(t1, t2):
        return (t2 - t1).seconds


if __name__ == '__main__':
    import dreambox.utils
    jenkins_config_path = '~/src/gitrepo/dreambox/python/dreambox-pythonlib/dreambox/etc'
    devops_jenkins = dreambox.jenkins.core.Jenkins('jenkins.ini', jenkins_config_path, 'stage-devops-jenkins')
    print('object type for devops_jenkins is %s' % type(devops_jenkins))
    print('jenkins configuration file: %s and section %s' % (devops_jenkins.config_file, devops_jenkins.section))
    print('jenkins server url: %s' % devops_jenkins.server)
    print('jenkins server user: %s' % devops_jenkins.user)
    print('--- testing Jenkins.create_jobinfos class method ---')
    jobinfos = Jenkins.create_jobinfos(devops_jenkins)
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
    dreambox.utils.print_structure(jobinfomap['environment_create'].job_config)
    print('')
    print('environment_create job info')
    dreambox.utils.print_structure(jobinfomap['environment_create'].job_info)
    print('')
    print('environment_create job parameters')
    dreambox.utils.print_structure(jobinfomap['environment_create'].parameters)
    print('')
    print('environment_create job next build number %s' % jobinfomap['environment_create'].next_build_number)
    print('')
    print('--- testing Jenkins.create_jobinfomap class method ---')
    print('')
    print('--- print out sorted job names ---')
    for job in sorted(jobinfomap.keys):
        print(job)
    print('--- print out sorted job names ---')
