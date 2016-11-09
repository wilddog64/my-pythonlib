from __future__ import print_function
from collections import Sequence
import dreambox.jenkins.core
import dreambox.utils
import jenkins
import os


class Job(object):
    def __init__(self, name, url, parameters):
        self._name = name
        self._url  = url
        self._parameters = parameters

    @property
    def name(self):
        return self._name

    @property
    def url(self):
        return self._url

    @property
    def parameters(self):
        return self._parameters

class JobInfo(object):
    def __init__(self, object):
        if not type(object) is dreambox.jenkins.core.Jenkins:
            raise TypeError('%s has to be a type of Jenkins' % object.__class__)
        self._parent     = object
        self._jenkins    = self._parent._server
        self._name       = ''
        self._url        = ''
        self._parameters = {}
        self._dry_run    = True
        self._has_dryrun = False
        self._workspace   = '/tmp'
        self._return_xml_python_struct = False

    @property
    def name(self):
        '''
        a propery return the name of the job
        '''
        return self._name

    @property
    def url(self):
        '''
        a property return the job url
        '''
        return self._url

    @property
    def parameters(self):
        '''
        a property to return the job parameters
        '''
        return self._parameters

    @property
    def dry_run(self):
        return self._dry_run

    @dry_run.setter
    def dry_run(self, value):
        self._dry_run = value

    @property
    def next_build_number(self):
        return self._jenkins.get_job_info(self.name)['nextBuildNumber']

    @next_build_number.setter
    def next_build_number(self, value):
        self._jenkins.set_next_build_number(self.name, value)

    @property
    def workspace(self):
        '''
        this property returns a current workspace for current
        object. It is mainly used for saving job
        '''
        return self._workspace

    @workspace.setter
    def workspace(self, value):
        self._workspace = value

    @property
    def return_xml_python_struct(self):
        return self._return_xml_python_struct

    @return_xml_python_struct.setter
    def return_xml_python_struct(self, value):
        self._return_xml_python_struct = value

    def build(self, args=None):
        '''
        trigger a jenkins job to build. The method
        takes a keyword parameters that should match
        what's defined in a given jenkins server.
        '''

        # clean up pass in arguments
        params = vars(args)
        del params['func']
        if not self.has_dryrun:
            self.dry_run = params['dry_run']
            del params['dry_run']
        del params['jenkins_user']
        del params['jenkins_user_pass']
        del params['jenkins_config_filepath']
        del params['jenkins_config_filename']
        del params['jenkins_config_section']
        del params['jenkins_url']
        del params['cache_timeout']
        if self.dry_run:
            print('triggering job %s' % self.name)
            print('with these arguments: (this is not sending to jenkins)')
            dreambox.utils.print_structure(params)
        else:
            self._jenkins.build_job(self.name, params)

    def disable(self):
        '''
        disable a jenkins job
        '''
        if self.dry_run:
            print('will disable job %s: ' % self.name)
        else:
            self._jenkins.disable_job(self.name)

    def enable(self):
        '''
        enable a jenkins job
        '''
        if self.dry_run:
            print('will enable job %s: ' % self.name)
        else:
            self._jenkins.enable_job(self.name)

    def copy(self, new_job_name):
        '''
        copy a given job with different name
        '''
        if self.dry_run:
            print('copy job %s as %s' % (self.name, new_job_name))
        else:
            self._jenkins.copy_job(self.name, new_job_name)

    def delete(self):
        '''
        delete a jenkins job
        '''
        if self.dry_run:
            print('deleting job %s' % self.name)
        else:
            self._jenkins.delete_job(self.name)

    @property
    def job_config(self):
        job_config = self._jenkins.get_job_config(self.name)

        if self.return_xml_python_struct:
            job_config = self._parent._load_xml(job_config)

        return job_config

    @property
    def job_info(self):
        return self._jenkins.get_job_info(self.name)

    @property
    def has_dryrun(self):
        return self._has_dryrun

    def save_job_config(self):
        if not os.path.exists(self.workspace):
            os.mkdir(self.workspace)
        filename = '%s.config.xml' % self.name
        fullpath = os.path.join(self.workspace, filename)
        print('write xml to %s' % fullpath)
        with open(fullpath, 'w') as configh:
            configh.write(self.job_config)

class JobInfos(Sequence):
    '''A container class wrapping a list with some extra functional magic, like head,
    tail, init, last, drop, and take. This allow us to handle JobInfos more
    easily'''

    def __init__(self, jobinfo=None):
        self._jobinfos = []

    def __len__(self):
        '''
        return the length of a sequence. This allow us to
        do len(JobInfos), where row is a type of Row
        '''
        return len(self._jobinfos)

    def __getitem__(self, index):
        # if index is of invalid type or value,
        # the list values will raise the error
        elements = None
        if isinstance(index, slice):
            elements = [self[idx] for idx in xrange(*index.indices(len(self)))]
        elif isinstance(index, int):
            if index < 0:
                index += len(self)
            if index < 0 or index >= len(self):
                raise IndexError('index %s is out of range' % index)
            elements = self._jobinfos[index]
        else:
            raise TypeError, 'Invalid argument type'

        return elements

    def __setitem__(self, index, value):
        '''
        overwrite element for a given index. It will raise an TypeError
        exception if value is not a type of JobInfo
        '''
        if type(value) is JobInfo:
            self._jobinfos[index] = value
        else:
            raise TypeError('invalid type. it has to be a type of JobInfo')

    def __delitem__(self, index):
        '''
        delete a element for a given index. The allow us to do
        del jobinfo[0], where jobinfo is a type of JobInfo
        '''
        del self._jobinfos[index]

    def __iter__(self):
        '''
        return an iterable object back. This allow us to do
        for jobinfo in jobinfos:  jobinfo is a type of JobInfo
          ...
        '''
        return iter(self._jobinfos)

    def __iadd__(self, other):
        '''
        allow us to do JobInfos += cell.

        * other is a instance of JobInfo object
        '''
        self._jobinfos.append(other)
        return self

    def append(self, other):
        '''
        appends an JobInfo into a JobInfos. This method will calcuate current columns
        in a JobInfos and update new cell.JobInfos property. It takes one parameter,

        * other is a type of JobInfo

        An TypeError exception will be thrown if other is not a type of JobInfo
        '''
        self._jobinfos.append(other)

    @property
    def head(self):
        # get the first element
        return self._jobinfos[0]

    @property
    def tail(self):
        # get all elements after the first
        return self._jobinfos[1:]

    @property
    def last(self):
        # get last element
        return self._jobinfos[-1]

    @property
    def length(self):
        return len(self)

class JobInfoMap(dict):
    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        if not key in self.__dict__:
            raise KeyError('unable to find %s in jenkins server' % key)
        return self.__dict__[key]

    def __len__(self):
        return len(self.__dict__)

    def items(self):
        return self.__dict__.items()

    def __iter__(self):
        return iter(self.__dict__)

    def __contains__(self, item):
        return item in self.__dict__

    def __cmp__(self, dict):
        return cmp(self.__dict__, dict)

    @property
    def keys(self):
        return self.__dict__.keys()

    @property
    def values(self):
        return self.__dict__.values()

    def clear(self):
        self._dict__.clear()

    def establish_object_connections(self, object=None):
        _jenkins = None
        if object is None:
            first     = self.values[0]._parent
            _jenkins  = jenkins.Jenkins(first.url,
                                       first.user,
                                       first.passwd)
        else:
            _jenkins = object._server

        for jobinfo in self:
            self[jobinfo]._jenkins = _jenkins
