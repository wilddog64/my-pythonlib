from __future__ import print_function
from funcy.seqs import chunks
from funcy.colls import select
import dreambox.ops.deployment
import pprint
import sys

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


def get_deployment_function_object(func_name):
    func_obj = getattr(dreambox.ops.deployment, func_name)

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
    for region, ingresses in ahash.items():
        chunk_table[region] = chunks(2, ingresses)

    key, values = None, None
    for region, ingresses in chunk_table.items():
        for ingress in ingresses:
            items = list(chunks(2, ingress))
            if items[0][0].lower().startswith(filterby.lower()):
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
