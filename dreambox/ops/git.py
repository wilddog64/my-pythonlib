#!/usr/bin/env python
from __future__ import print_function
import dreambox.ops.git_client
from docopt import docopt
import dreambox.utils

def dispatch_command(argv=None):
    ''' usage: ops git-client <command> [<args>...]

    '''
    args = docopt(dispatch_command.__doc__,
                  version='ops aws 0.0.1',
                  options_first=True,
                 )
    argv = [args['<command>']] + args['<args>']
    print('arguments %s' % argv)
    command = args['<command>']
    print('command receive is %s' % command)

    func = dreambox.utils.get_function_object(dreambox.ops.git_client, command)
    func(argv)

