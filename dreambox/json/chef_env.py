from __future__ import print_function
import json
import os
import sys
import dreambox.utils

def load_chef_environment_attributes(json_file, section='default_attributes'):
    dirname = os.path.dirname(json_file)
    filename = os.path.basename(json_file)
    with open(json_file, 'r') as jsonf:
        json_result = json.loads(jsonf.read())

    return (json_result[section], dirname, filename)


def get_delta_set(from_json_env=None, to_json_env=None):
    '''
get_delta_set is a function that will compare two dictionary objects
and return an updated dict.  This function takes two parameters,

* from_json_env is a base json block
* to_json_env is a json block that compares with base json block

return a updated dictionary: to_json_env if there are difference between the
two; otherwise, return None
    '''
    # find out what cookbooks are not in the target json file
    key_mismatch = from_json_env.viewkeys() - to_json_env.viewkeys()
    # if key_difference:
    #     print('keys are different: ', file=sys.stderr)
    #     dreambox.utils.print_structure(key_difference)
    #     to_json_env.update((key, from_json_env)
    #        for key in from_json_env.viewkeys() - to_json_env.viewkeys())
    #     key_mismatch = to_json_env

    # find different values in target hash by comparsion with source one
    delta = [elem for elem in from_json_env
                if not (from_json_env[elem] == to_json_env[elem])]

    return key_mismatch, delta


def load_chef_environment_file(json_file):
    with open(json_file, 'r') as jsonf:
        json_result = json.loads(jsonf.read())

    return json_result

def load_all_chef_environment_files(json_files):
    json_file_hash = {}
    for json_file in json_files:
        file_basename = os.path.basename(json_file).split('.')[1]
        json_file_hash[file_basename] = load_chef_environment_file(json_file)

    return json_file_hash


def update_environments(from_file='production.json', search_key=None, to='all', update=True):

    if search_key is None:
        search_key = ['account.version',
                      'api.subversion',
                      'dreamboxcom.subversion',
                      'edex.version',
                      'galactus.version',
                      'galactus2.version',
                      'lessons.key',
                      'magneto.version',
                      'product.build_key']
    # if to is all, then list all known environment json files
    if type(to) is str and to.lower() == 'all':
        to = ['stage1.json', 'stage2.json', 'stage3.json',
              'stage4.json', 'stage5.json', 'stage6.json',
              'stage7.json', 'stage8.json', 'stage9.json',
              'production.json']
    # filter out from_file
    to_list = filter(lambda x: x.lower() != from_file.lower(), to)
    dreambox.utils.print_structure(to_list)
    # dreambox.utils.print_structure(to_list)

    # load desired chef environment attributes from a file stored in from_file
    attribute_tuple = load_chef_environment_attributes(from_file)

    # obtain a path information and construct a full path list
    pathinfo = attribute_tuple[1]
    to_list_pathinfo = map(lambda x: os.path.join(pathinfo, x), to_list)
    # dreambox.utils.print_structure(to_list_pathinfo)

    # now find the values that can be used to update other environment files,
    # and store them in a hashinfo table
    hashinfo = {}
    hashinfo[attribute_tuple[-2:]] = dreambox.utils.get_values_from_hashtable(
        attribute_tuple[0],
        search_key)

    if update:
        print('updating chef environment file', file=sys.stderr)
        __update_environment_files(to_list_pathinfo, hashinfo[attribute_tuple[-2:]])

    return hashinfo


def __update_environment_files(update_file_list=None, update_values=None):
    json_doc = None
    need_update = False
    for update_file in update_file_list:
        json_object = load_chef_environment_file(update_file)
        for update_key, update_value in update_values.items():
            (json_doc, need_update) = __update_json_object(update_file,
                                                           json_object,
                                                           update_key,
                                                           update_value)
            if need_update:
                with open(update_file, 'w') as updateh:
                    updateh.write(json.dumps(json_doc, sort_keys=True, indent=2, separators=(',', ': ')))


def __update_json_object(filename, json_object, key, value):
    keys = key.split('.')
    # dreambox.utils.print_structure(key)
    # print('type is {}'.format(type(value)))
    app = keys[0]
    should_write_to_file = False
    if type(value) is dict:
        inner_keys = value.keys()
        if app in json_object['default_attributes']:
            new_value1 = value[inner_keys[0]]
            new_value2 = value[inner_keys[1]]
            old_value1 = json_object['default_attributes'][keys[0]][keys[1]][inner_keys[0]]
            old_value2 = json_object['default_attributes'][keys[0]][keys[1]][inner_keys[1]]
            if new_value1 != old_value1:
                json_object['default_attributes'][keys[0]][keys[1]][inner_keys[0]] = new_value1
                should_write_to_file = True
            else:
                print('current file [{}] no need update {}.{}.{} is {} '.format(filename,
                       keys[0],
                       keys[1],
                       inner_keys[0],
                       json_object['default_attributes'][keys[0]][keys[1]][inner_keys[0]]))

            if new_value2 != old_value2:
                json_object['default_attributes'][keys[0]][keys[1]][inner_keys[1]] = new_value2
                should_write_to_file = True
            else:
                print('current file [{}] no need update: {}.{}.{} is {}'.format(filename,
                       keys[0],
                       keys[1],
                       inner_keys[1],
                       json_object['default_attributes'][keys[0]][keys[1]][inner_keys[1]]))

    elif type(value) is unicode:
        if app in json_object['default_attributes']:
            old_value = json_object['default_attributes'][keys[0]][keys[1]]
            if value != old_value:
                json_object['default_attributes'][keys[0]][keys[1]] = value
                should_write_to_file = True
            else:
                print('current file [{}] value for  default_attributes.{}.{} does not change]'.format(filename, keys[0], keys[1]))

    return (json_object, should_write_to_file)

if __name__ == '__main__':
    json_file = '/Users/chengkai.liang/src/gitrepo/dreambox/chef/environments/production.json'

    print('testing load_chef_environment_attributes', file=sys.stderr)
    print('-------------------------------------', file=sys.stderr)
    production_json = load_chef_environment_attributes(json_file)
    dreambox.utils.print_structure(production_json)
    print('end testing load_chef_environment_attributes', file=sys.stderr)
    print('-------------------------------------', file=sys.stderr)
    print()
    print('testing update_environment', file=sys.stderr)
    print('--------------------------', file=sys.stderr)
    search_info = update_environments(from_file=json_file, to=['stage4'], update=False)
    dreambox.utils.print_structure(search_info)
    print('end testing update_environment', file=sys.stderr)
    print('------------------------------', file=sys.stderr)
    print()
    print('testing load_chef_environment_attributes', file=sys.stderr)
    print('----------------------------------------', file=sys.stderr)
    cookbook_versions = load_chef_environment_attributes(json_file=json_file, section='cookbook_versions')
    dreambox.utils.print_structure(cookbook_versions)
    print('end testing load_chef_environment_attributes', file=sys.stderr)
    print('--------------------------------------------', file=sys.stderr)
    print()
    print('testing get_delta_set', file=sys.stderr)
    print('---------------------------', file=sys.stderr)
    prod_json = '/Users/chengkai.liang/src/gitrepo/dreambox/chef/environments/production.json'
    stage1_json =  '/Users/chengkai.liang/src/gitrepo/dreambox/chef/environments/stage1.json'
    prod_json, prod_dirname, prod_filename = load_chef_environment_attributes(prod_json, section='cookbook_versions')
    stage1_json, stage1_dirname, stage1_filename = load_chef_environment_attributes(stage1_json, section='cookbook_versions')
    missing_cookbooks, mismatch_values = get_delta_set(prod_json, stage1_json)
    if missing_cookbooks:
        print('keys looks different are: ', file=sys.stderr)
        dreambox.utils.print_structure(missing_cookbooks)
    else:
        print('no mismatch keys found', file=sys.stderr)

    if mismatch_values:
        print('values for these are different', file=sys.stderr)
        dreambox.utils.print_structure(mismatch_values)
    print('testing compare_differences', file=sys.stderr)
    print('---------------------------', file=sys.stderr)
