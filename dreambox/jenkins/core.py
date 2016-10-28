from __future__ import print_function
import dreambox.config.core as inifile
import jenkins
from xmljson import BadgerFish
from xml.etree.ElementTree import fromstring
import json
import dreambox.jenkins
import dreambox.jenkins.JobInfo
from dreambox.jenkins.parameter import Parameter, ParameterMap

import os
import datetime

# if cPickle is available the include it; otherwise
# use pure Python implementation
try:
    import cPickle as pickle
except:
    import pickle

class JenkinsParameterError(Exception):
    def __init__(self, message):
        super(Exception, self).__init__(message)

class Jenkins(object):

    def __init__(self, jenkins_url='',
                       jenkins_user='',
                       jenkins_pass='',
                       config_file='',
                       config_file_path='',
                       section=''):
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
        self._user           = jenkins_user if jenkins_user else self._config['user']
        self._passwd         = jenkins_pass if jenkins_pass else self._config['password']
        self._url            = jenkins_url if jenkins_url else self._config['url']
        self._jobs           = dict()
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
        if len(self._jobs) == 0:
            for job in self._server.get_all_jobs():
                job_name             = job['name']
                job_url              = job['url']
                job_parameters       = self._get_job_parameters(job_name)
                self._jobs[job_name] = dreambox.jenkins.JobInfo.Job(job_name, job_url, job_parameters)
        return self._jobs

    @property
    def name(self):
        '''
        an alias for the self.section property
        '''
        return self._name

    def _get_job_parameters(self, job_name=''):
        params                 = {}
        parameters             = ParameterMap()
        job_property           = self._server.get_job_info(job_name)['property']
        parameter_definitions  = None
        if job_property and 'parameterDefinitions' in job_property[0]:
            parameter_definitions = job_property[0]['parameterDefinitions']
            for p in parameter_definitions:
                p_name          = p['name']
                p_type          = p['type']
                p_default       = ''
                p_value         = ''
                params['name']  = p['name']
                if 'defaultParameterValue' in p and \
                   'value' in p['defaultParameterValue']:
                    p_default = p['defaultParameterValue']['value']
                if 'Choice' in p_type:
                    p_value = p['choices']
                else:
                    p_value = p['value'] if 'value' in p else ''
                p_description = p['description']
                p = Parameter(p_name,
                              p_value,
                              p_default,
                              p_type,
                              p_description)
                parameters[p_name] = p

        else:
            print('job name %s' % job_name)
            pass

        return parameters

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
    def create_jobinfomap(self, object=None, cache_timeout=5):
        '''
        will create a JobInfoMap container object. The method takes one parameter

        * object which is a type of JobInfo

        the class method will cache the JobInfoMap object via cPickle. it will also
        invalidate the cache file in 5 minutes.
        '''
        load_from_pickle = False
        def _create_jobinfomap():
            jobinfomap = dreambox.jenkins.JobInfo.JobInfoMap()
            for job in object._get_jobs():
                jobinfo                  = dreambox.jenkins.JobInfo.JobInfo(object)
                jobinfo._name            = job
                jobinfo._url             = object._get_jobs()[job].url
                parameters               = object._get_jobs()[job].parameters
                jobinfo._parameters      = parameters
                jobinfomap[jobinfo.name] = jobinfo
                if 'dry_run' in parameters:
                    jobinfo._has_dryrun = True
            return jobinfomap

        current_dir = os.path.curdir
        workspace   = os.path.join(current_dir, 'tmp')
        if not os.path.exists(workspace):
            print('create directory %s' % workspace)
            os.mkdir(workspace)
        pickle_file       = os.path.join(workspace, 'obj.pickle')
        pickle_filehandle = None
        jobinfomap        = None
        pickle_filehandle = None
        if os.path.exists(pickle_file) and \
                Jenkins.timediff_in_secs(Jenkins.mdate(pickle_file),
                        datetime.datetime.now()) > (cache_timeout * 60):
            print('pickle file expired, regenerating it')
            os.unlink(pickle_file)

        try:
            if not os.path.exists(pickle_file):
                pickle_filehandle = open(pickle_file, 'w+b')
            else:
                pickle_filehandle = open(pickle_file, 'r+b')
                load_from_pickle  = True
            jobinfomap = None
            if load_from_pickle:
                print('reloading object')
                jobinfomap = pickle.load(pickle_filehandle)
                jobinfomap.establish_object_connections()
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
    devops_jenkins = dreambox.jenkins.core.Jenkins(config_file='jenkins.ini', config_file_path=jenkins_config_path, section='stage-devops-jenkins')
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
    print(type(jobinfomap.environment_create.parameters))

    print('environment_create job next build number %s' % jobinfomap['environment_create'].next_build_number)
    print('')
    print('--- testing Jenkins.create_jobinfomap class method ---')
    print('')
    print('--- print out sorted job names ---')
    for job in sorted(jobinfomap.keys):
        print(job)
    print('--- print out sorted job names ---')
    print('')
    environment_create_parameters = jobinfomap.environment_create.job_info['property'][0]['parameterDefinitions']
    dreambox.utils.print_structure(environment_create_parameters)
    for jobinfo in jobinfomap:
        if jobinfomap[jobinfo].has_dryrun:
            print('%s has dry_run property' % jobinfo)
