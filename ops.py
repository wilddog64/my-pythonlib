#!/usr/bin/env python

import argparse
import yaml
import os

def loadYamlConfig(yamlConfigFile):
    '''
loadYamlConfig is a function that will load the yaml configuration, conf.yml.
This function takes one parameter,

* yamlConfigFile is a yml configuration file.

loadYamlConfig return a python dict object when successfully load a yaml
configuration file.

Note: the function assume conf.yml file exist in current script ./etc directory.
you will need to make sure that ./etc/conf.yml exists.
    '''
    scriptDir = os.path.dirname(os.path.realpath(__file__))
    scriptEtc = os.path.join(scriptDir, 'dreambox', 'etc')
    yamlConfigFilePath = os.path.join(scriptEtc, yamlConfigFile)
    with open(yamlConfigFilePath, 'r') as yamlh:
        config = yaml.load(yamlh)

    return config

def createSubCommandLineOptions(yamlConfigFile):
    '''
createSubCommandLineOptions is a function that builds sub-command command line
otions.  This function depends on argparse and pyYaml to build a usable command
line options.  The function take only one parameter,

* config which is a dict object return by a pyYaml load function

createSubCommandLineOptions will return a parsed args object back to caller
    '''
    config = loadYamlConfig(yamlConfigFile)             # load yaml configuration file
    cmdOptParser = argparse.ArgumentParser(prog='ops',  # create a main command line parser
                                           description='operation common execution tasks')
    subParsers = cmdOptParser.add_subparsers()          # create sub-parsers
    for app, config in config.items():                  # loop through a dict object
        if 'position' in config:
            positionArgs = config['position']           # positional arguments dict
        kwArgs = config['key-values']                   # key/value dict object
        helpMsg = config['help']
        func = config['func']                           # a sub-command entry, this is a python function
        __buildCmdOptions(subParsers,                   # now build sub-command command line options
                          app,
                          helpMsg,
                          positionArgs,
                          kwArgs,
                          func)

    args = cmdOptParser.parse_args()                    # create args object
    args.func(args)                                     # pass args to the function


def __buildCmdOptions(subParsers=None,
                      app=None,
                      helpMsg=None,
                      positionArgs=None,
                      kwArgs=None,
                      func=None):

    # first we create a sub-parser object
    subParser = subParsers.add_parser(app, help=helpMsg)

    # handling position arguments
    for args in positionArgs:
        if args is not None:
            for positionArg, positionHelp in args.items():
                if positionArg and 'help' in positionHelp:
                    subParser.add_argument(positionArg, help=positionHelp['help'])

    # handling key-value arguments
    for optName, optSettings in kwArgs.items():
        optShort = '-%s' % optSettings['short']
        optLong = '--%s' % optName
        optDefault = optSettings['default']
        optType = optSettings['type']
        optDest = optSettings['dest']
        optHelp = optSettings['help']
        subParser.add_argument(optShort,
                               optLong,
                               type=optType,
                               dest=optDest,
                               help=optHelp,
                               default=optDefault)

    # setup a hook function
    subParser.set_defaults(func=func)

if __name__ == '__main__':
    createSubCommandLineOptions('conf.yml')
