from funcy.seqs import chunks
import dreambox.ops.deployment
import pprint

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

