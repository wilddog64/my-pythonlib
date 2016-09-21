from __future__ import print_function
from collections import Sequence
from dreambox.jenkins import core

class JobInfo(object):
    def __init__(self, object):
        if not type(object) is core.Jenkins:
            raise TypeError('%s has to be a type of Jenkins' % object.__class__)
        self._server = object
        self._name        = ''
        self._url         = ''
        self._parameters  = []

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

    def build_job(self, **params):
        '''
        trigger a jenkins job to build. The method
        takes a keyword parameters that should match
        what's defined in a given jenkins server.
        '''
        self._server.build_job(self.name, params)

class JobInfos(Sequence):
    '''A Row class wrapping a list with some extra functional magic, like head,
    tail, init, last, drop, and take. This allow ups to handle Excel row more
    easily'''
    
    def __init__(self, jobinfo=None):
        self._jobinfos   = []

    def __len__(self):
        '''
        return the length of a sequence. This allow us to
        do len(row), where row is a type of Row
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
        del row[0], where row is a type of Row
        '''
        del self._jobinfos[index]
    
    def __iter__(self):
        '''
        return an iterable object back. This allow us to do
        for cell in row:  # row is a type of Row
          ...
        '''
        return iter(self._jobinfos)
   
    def __iadd__(self, other):
        '''
        allow us to do row += cell. This method will increment a column
        value and append cell into a list. It takes one parameter,

        * other is a instance of Cell object
        '''
        self._jobinfos.append(self._add_cell(other))
        return self

    def append(self, other):
        '''
        appends an Cell into a row. This method will calcuate current columns
        in a row and update new cell.row property. It takes one parameter,

        * other is a type of Cell

        An TypeError exception will be thrown if other is not a type of Cell
        '''
        self._jobinfos.append(self._add_cell(other))

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
    def columns(self):
        '''
        return current number of columns in a row
        '''
        return self._columns

    @property
    def row(self):
        '''
        return current row position. This is a read
        only property
        '''
        return self._row

    @row.setter
    def row(self, value):
        self._row = value

    @property
    def column(self):
        '''
        return the current column in a row
        '''
        return self._column

    @column.setter
    def column(self, value):
        self._column = value

    def drop(self, n):
        # get all elements except first n
        return self._jobinfos[n:]

    def take(self, n):
        # get first n elements
        return self._jobinfos[:n]

    def range(self, start=0, end=0, row_abs=False, col_abs=False):
        '''
        return a range in an A1 notation. The
        method takes two parameters,

        * start is the first cell in the row
        * end is the last cell in the row
        * row_abs is flag that tells if range to return row absolute address or not. Default is false
        * col_abs is flag that tells if range to return column absolute address or not. Default is false

        if start and end are 0, then return the
        A1 address for entire row
        '''

        template = '%s:%s'
        A1_address = None
        if start == 0 and end == 0:
            A1_address = template % (self.head.A1(row_abs=row_abs, col_abs=col_abs),
                                     self.last.A1(row_abs=row_abs, col_abs=col_abs))
        else:
            A1_address = template % (self[start].A1(row_abs=row_abs, col_abs=col_abs),
                                     self[end].A1(row_abs=row_abs, col_abs=col_abs))

        return A1_address

    def _add_cell(self, other):
        '''
        add Cell object into a row collection. Take one parameter

        * other is a type of Cell
        '''
        if type(other) is JobInfo:
            self._columns += 1
            # make sure Cell add to row has are in the same row
            if self._column == -1:
                other.row = self._row
                if other.column == 0:
                    other.column = self._column
            else:
                if len(self._jobinfos) > 0:
                    if other.column == 0:
                        other.column = self.last.column + 1
                    other.row = self._row
                else:
                    if other.column == 0:
                        other.column = self._column
                    other.row = self._row
        else:
            raise TypeError('invalid type. it has to be a type of Cell')

        return other

if __name__ == '__main__':
    jenkins_svr = core.Jenkins('jenkins.ini', 'stage-jenkins-ng')
