from __future__ import print_function
import ConfigParser
import os


def load_ini_config(config_file='', config_file_path=''):
    '''
    load an ini configuration file from within a directory
    '''
    script_dir = os.path.dirname(os.path.realpath(__file__))

    script_etc = ''
    if config_file_path != '':
        script_etc = os.path.expanduser(config_file_path)
    else:
        script_etc = os.path.join(script_dir, '..', 'etc')
    jenkins_config_path = os.path.join(script_etc, config_file)
    config              = ConfigParser.ConfigParser()
    config.read(jenkins_config_path)

    return config

def config_section_map(config_file='', config_file_path='', section_name=''):
    '''
    provide an easy way to access option in an ini file section. This
    function accepts two parameters

    * config_file is a name of the ini configuration file. Note, we only
      need the name of the file, not the full path. The ini file should
      store at the script directory's etc folder

    * section_name is a section name in a ini file

    the function will return a hash that contains all the options for a
    given section
    '''

    config = load_ini_config(config_file, config_file_path)
    section = {}
    for option in config.options(section_name):
        section[option] = config.get(section_name, option)

    return section


if __name__ == '__main__':
   print('--- testing config_section_map ---')
   print('jenkins user %s: ' % config_section_map(config_file='jenkins.ini',
                                                  section_name='stage-devops-jenkins')['user'])
   print('jenkins url %s: ' %config_section_map(config_file='jenkins.ini',
                                                section_name='stage-devops-jenkins')['url'])
   print('--- testing config_section_map ---')
   print('')
   jenkins_config_path = '~/src/gitrepo/dreambox/python/dreambox-pythonlib/dreambox/etc'
   print('jenkins user %s' % config_section_map(config_file='jenkins.ini',
                                                config_file_path=jenkins_config_path,
                                                section_name='stage-devops-jenkins')['user'])
