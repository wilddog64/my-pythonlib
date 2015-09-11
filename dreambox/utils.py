from __future__ import print_function
from funcy.seqs import chunks
from itertools import count
from time import strftime

import time
import re
import pprint
import sys
import os
import pwd

# make_hash_of_hashes will make an array of hashes from a given list by these
# steps,
#
#   1. create a pairwise list of tuples
#   2. transfer turple into a list
#   3. create a hash where key is the first element, and value is the reset
#   4. append hash to a list
#
# the function takes the following parameters,
#
#   my_list: a valid python list
#
# return a list of hashes upon a succesful call
def make_hash_of_hashes(my_list):
    # turple = zip(my_list[::2], my_list[1::2])
    chunks_list = chunks(2, my_list)
    result = {}
    for item in chunks_list:
        items = list(item)
        result[items[0][0]] = items[1]
    return result


def get_function_object(library=None, func_name=None):

    func_obj = None
    if func_name in dir(library):
       func_obj = getattr(library, func_name)

    return func_obj


def print_structure(object=None, debug=True):
    pp = pprint.PrettyPrinter(indent=3)

    if debug:
        pp.pprint(object)


def filter_list_by(my_dict=None, myfilter=None):

    if my_dict is None:
        my_dict = {}
    results = {}
    if not myfilter is None:
        for region, lists in my_dict.items():
            results[region] = [p for p in lists if p.capitalize().startswith(myfilter.capitalize())]
    else:
        results = my_dict
    return results


def create_hashtable_from_hashes(ahash=None, filterby=None):
    chunk_table = {}
    hash_tables = {}
    hash_table = {}
    regex_pattern = r'{0}\b'.format(filterby)
    m = re.compile(regex_pattern, re.I)
    for region, ingresses in ahash.items():
        chunk_table[region] = chunks(2, ingresses)

    key, values = None, None
    for region, ingresses in chunk_table.items():
        for ingress in ingresses:
            items = list(chunks(2, ingress))
            # if items[0][0].lower().startswith(filterby.lower()):
            if m.match(items[0][0]):
                key = items[0][0]
                values = items[0][1]
                hash_table[key] = values
                hash_tables[region] = hash_table
            else:
                key = items[0][0]
                values = grep(items[0][1], filterby)
                if values:
                    hash_table[key] = values
                    hash_tables[region] = hash_table


    return hash_tables


def grep(input_list=None, search_str=None):
    if search_str is None:
        return input_list

    grep_result = []
    for this_input in input_list:
        if search_str in this_input:
            grep_result.append(this_input)

    return grep_result


def generate_buzz(period):
    nexttime = time.time() + period
    for i in count():
        now = time.time()
        sleep_time = nexttime - now
        if sleep_time > 0:
            time.sleep(sleep_time)
            nexttime += period
        else:
            nexttime = now + period
        yield i, nexttime


def chunk_list(seq=None, chunk_size=2):
    return list(chunks(chunk_size, seq))


def get_epoch_time():
    '''
get_epoch_time return current epoch time
    '''

    return str((int(expiration) * 86400) + int(time.time()))


def dict_slice(d, keys):
    '''
a python function that perform a similar function like perl's hash slicing.  It
takes the following two parameters,

d is a python dictionary object
keys a a list of hash keys to slice
    '''

    return map(d.get, keys)


def get_values_from_hashtable(hash=None, search_list=None):
    '''
get_values_from_hashtable is a function that will return a key value of a hash.
This function take two parameters,

hash: a hash to search for
search_list a list of key to search against a given hash.  The key has to be
presented in java property format, x.y.z.

The function will return a key-value back in a hash.
    '''


    hashtable = {}
    for search_key in search_list:
        elements = search_key.split('.')
        hashtable[search_key] = hash[elements[0]][elements[1]]

    return hashtable


def to_bool(bool_string):
    boolean = None
    if bool_string is True or bool_string is False:
        boolean = bool_string
    else:
        bool_string = str(bool_string).strip().lower()
        boolean = not bool_string in ['false', 'f', 'n', '0', '']

    return boolean

def get_current_user():
    return pwd.getpwuid(os.getuid()).pw_name


def current_timestamp():
    return strftime('%Y-%m-%d_%H-%M-%S')

if __name__ == '__main__':
    print('testing generate_buzz')
    print('=====================')
    buzz = generate_buzz(3)
    print('current time %s' % time.time())
    buzz.next()
    print('buzz time %s' % time.time())

    print('testing dict_slice -- dictionary slice')
    dict_obj = {
        'a': ['a', 'b', 'c'],
        'b': [1, 2, 3],
        'c': ['ab', 'cd', 'ef'],
        'd': [92, 93, 95],
        'f': [{'a': [12, 13]}, {'c': 9}],
    }
    hash_slice = dict_slice(dict_obj, ['a', 'b', 'f'])
    print_structure(hash_slice)


def debug_print(debugFlag=True, message=''):
    if debugFlag:
        print(message, file=sys.stderr)
