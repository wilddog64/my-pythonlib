from __future__ import print_function

class Parameter(object):
    def __init__(self, name, value, default, atype, description):
        self.name        = name
        self.value       = value
        self.default     = default
        self.type        = atype
        self.description = description


class ParameterMap(dict):
    def __setitem__(self, key, item):
        self.__dict__[key] = item

    def __getitem__(self, key):
        return self.__dict__[key]

    def __len__(self):
        return len(self.__dict__)

    def __items__(self):
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

