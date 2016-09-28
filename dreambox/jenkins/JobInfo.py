from __future__ import print_function
from collections import Sequence
import dreambox.jenkins.core

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

    def build_job(self, **params):
        '''
        trigger a jenkins job to build. The method
        takes a keyword parameters that should match
        what's defined in a given jenkins server.
        '''
        if not params:
            params = self.parameters
        if self.dry_run:
            print('trigger job %s' % self.name)
        else:
            self._jenkins.build_job(self.name, params)

    def disable_job(self):
        '''
        disable a jenkins job
        '''
        if self.dry_run:
            print('will disable job %s: ' % self.name)
        else:
            self._jenkins.disable_job(self.name)

    def enable_job(self):
        '''
        enable a jenkins job
        '''
        if self.dry_run:
            print('will disable job %s: ' % self.name)
        else:
            self._jenkins.enable_job(self.name)

    def copy_job(self, new_job_name):
        '''
        copy a given job with different name
        '''
        if self.dry_run:
            print('copy job %s as %s' % (self.name, new_job_name))
        else:
            self._jenkins.copy_job(self.name, new_job_name)

    def delete_job(self):
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
        return self._parent._load_xml(job_config)

    @property
    def job_info(self):
        return self._jenkins.get_job_info(self.name)

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
            raise KeyError('unable to find %s in container' % key)
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
