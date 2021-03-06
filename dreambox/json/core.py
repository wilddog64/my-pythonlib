from __future__ import print_function
import json
import os
import sys
import dreambox.utils

def load_chef_environment_attributes(json_file):
    dirname = os.path.dirname(json_file)
    filename = os.path.basename(json_file)
    with open(json_file, 'r') as jsonf:
        json_result = json.loads(jsonf.read())

    return (json_result['default_attributes'], dirname, filename)


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


def update_environments(from_file='production.json', search_key=None, to='all'):

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
    if to.lower() == 'all':
        to = ['stage1.json', 'stage3.json', 'stage4.json',
              'stage5.json', 'stage6.json', 'stage8.json',
              'production.json']
    # filter out from_file
    to_list = filter(lambda x: x.lower() != from_file.lower(), to)
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

    __update_environment_files(to_list_pathinfo, hashinfo[attribute_tuple[-2:]])

    return hashinfo


def __update_environment_files(update_file_list=None, update_values=None):
    for update_file in update_file_list:
        json_object = load_chef_environment_file(update_file)
        for update_key, update_value in update_values.items():
            # dreambox.utils.print_structure(update_key)
            # dreambox.utils.print_structure(update_value)
            __update_environment_file(update_file, json_object, update_key, update_value)


def __update_environment_file(filename, json_object, key, value):
    keys = key.split('.')
    # dreambox.utils.print_structure(key)
    # print('type is {}'.format(type(value)))
    app = keys[0]
    if type(value) is dict:
        inner_keys = value.keys()
        if app in json_object['default_attributes']:
            new_value1 = value[inner_keys[0]]
            new_value2 = value[inner_keys[1]]
            old_value1 = json_object['default_attributes'][keys[0]][keys[1]][inner_keys[0]]
            old_value2 = json_object['default_attributes'][keys[0]][keys[1]][inner_keys[1]]
            if new_value1 != old_value1:
                print('current file [{}] update {}.{}.{} to {} '.format(filename,
                       keys[0],
                       keys[1],
                       inner_keys[0],
                       new_value1))
            else:
                print('current file [{}] no need update {}.{}.{} is {} '.format(filename,
                       keys[0],
                       keys[1],
                       inner_keys[0],
                       json_object['default_attributes'][keys[0]][keys[1]][inner_keys[0]]))


            if new_value2 != old_value2:
                print('current file [{}] update {}.{}.{} to {} '.format(filename,
                       keys[0],
                       keys[1],
                       inner_keys[1],
                       new_value2))
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
                print('[update {}] default_attributes.{}.{} to {}'.format(filename, keys[0], keys[1], value))
            else:
                print('current file[{}] value for  default_attributes.{}.{} does not change]'.format(filename, keys[0], keys[1]))


def write_json_to_file(jsonFile=None, jsonObj=None):
    '''
write_json_to_file is function that will write json object to a file.  The
function takes two parameters,

* jsonFile is a file that this function will write to. If only filename pass in, the
  file will be written to current directory
* jsonObj is an json object or document to write to a given file
    '''
    with open(jsonFile, 'w') as fileHandle:
        fileHandle.write(json.dumps(jsonObj,
                                    sort_keys=True,
                                    indent=2,
                                    separators=(',', ': ')))


def py2json(pyobj=None):
    return json.dumps(pyobj,
                      sort_keys=True,
                      indent=2,
                      separators=(',', ': '))


def json2py(json_blob=None):
    return json.loads(json_blob)


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
    search_info = update_environments(from_file=json_file)
    # dreambox.utils.print_structure(search_info)
    print('end testing update_environment', file=sys.stderr)
    print('------------------------------', file=sys.stderr)
    print('testing json2py', file=sys.stderr)
    print('---------------', file=sys.stderr)
    py_result = json2py('{"us-east-1": "east-databag"}')
    dreambox.utils.print_structure(py_result)
    print('end testing json2py', file=sys.stderr)
    print('---------------', file=sys.stderr)
