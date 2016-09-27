from __future__ import print_function
from collections import Sequence
import dreambox.jenkins.core

class JobInfo(object):
    def __init__(self, object):
        if not type(object) is dreambox.jenkins.core.Jenkins:
            raise TypeError('%s has to be a type of Jenkins' % object.__class__)
        self._server     = object
        self._jenkins    = object._server
        self._name       = ''
        self._url        = ''
        self._parameters = {}
        self._dry_run    = False

    @property
    def name(self):
        '''
        a propery return the name of the job
        '''
        return self._name

    @name.setter
    def name(self, value):
        '''
        a property set the name of the job
        '''
        self._name = value

    @property
    def url(self):
        '''
        a property return the job url
        '''
        return self._url

    @url.setter
    def url(self, value):
        '''
        a property allow to set the job url
        '''
        self._url = value

    @property
    def parameters(self):
        '''
        a property to return the job parameters
        '''
        return self._parameters

    @parameters.setter
    def parameters(self, value):
        '''
        a property to set the job parameters
        '''
        self._parameters = value

    @property
    def dry_run(self):
        return self._dry_run

    @dry_run.setter
    def dry_run(self, value):
        self._dry_run = value


    def build_job(self, **params):
        '''
        trigger a jenkins job to build. The method
        takes a keyword parameters that should match
        what's defined in a given jenkins server.
        '''
        if not params:
            params = self.parameters
        self._server.build_job(self.name, params)

    def disable_job(self):
        '''
        disable a jenkins job
        '''
        self._server.disable_job(self.name)

    def enable_job(self):
        '''
        enable a jenkins job
        '''
        self._server.enable_job(self.name)

    def copy_job(self, new_job_name):
        '''
        copy a given job with different name
        '''
        self._jenkins.copy_job(self.name, new_job_name)

    def delete_job(self):
        '''
        delete a jenkins job
        '''
        self._jenkins.delete_job(self.name)

    def get_job_config(self):
        job_config = self._jenkins.get_job_config(self.name)
        return self._server._load_xml(job_config)

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
        if index > len(self):
            raise IndexError('index %s is out of range' % index)
        return self._jobinfos[index]
    
    def __setitem__(self, index, value):
        '''
        overwrite element for a given index. It will raise an TypeError
        exception if value is not a type of Cell
        '''
        if type(value) is JobInfo:
            self._jobinfos[index] = value
        else:
            raise TypeError('invalid type. it has to be a type of Cell')
    
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

        * other is a instance of Cell object
        '''
        self._jobinfos.append(other)
        return self

    def append(self, other):
        '''
        appends an Cell into a JobInfos. This method will calcuate current columns
        in a JobInfos and update new cell.JobInfos property. It takes one parameter,

        * other is a type of Cell

        An TypeError exception will be thrown if other is not a type of Cell
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
