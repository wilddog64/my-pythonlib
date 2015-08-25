from __future__ import print_function
import dreambox.git.client as Git
import dreambox.utils
import os
import sys
from docopt import docopt
import docopt

from dreambox.json.chef_env import update_environments

def __merge_updated_chef_environment_file(from_env='production.json',
                                          to_env='stage1',
                                          repo_path='/tmp',
                                          repo_name='chef-environments',
                                          repo_url='git@github.com:wilddog64/chef-environments.git',
                                          dry_run=False):
    '''
merge_updated_chef_environment_file is a function taht will update chef envirnoment file from
one file to another in a newly create branch, then merge that branch into master.  The function
takes the following parameters,

* from_env is a chef environment that will be used to update other chef environment
* to_env is a chef environment that will be updated
* repo_path is a path that repo will be created at
* repo_name is a name of repo
* repo_url is a git url that this function will clone repo from
    '''
    currentUser = dreambox.utils.get_current_user()
    currentTimestamp = dreambox.utils.current_timestamp()
    appPath = os.path.join(repo_path, repo_name)
    envFilePath = os.path.join(appPath, from_env)
    Git.clone_repo_to_local(repo_url,
                            repo_path,
                            app_name=repo_name,
                            recurse_submodules=False,
                            force_remove_repo=True)
    branchName = 'production'
    commitMessage = 'automic merge %s into master by %s at %s' % (branchName,
                                                                  currentUser,
                                                                  currentTimestamp)
    Git.create_branch(branch_name=branchName,
                      repo_path=appPath,
                      create_and_switch=True)
    update_environments(envFilePath, to_env)
    Git.merge_branch(repo_path=appPath,
                     from_branch=branchName,
                     to_branch='master',
                     merge_message=commitMessage)
    Git.push_ref(repo_path=appPath,
                 dry_run=dry_run)


def clone_env_apps(argv=None):
    '''
Usage: git-client clone_env_apps [options] <from_env> <to_env>

    -p, --repo-path=<repo_path>  a path where repo should clone to [default: /tmp]
    -o, --repo-name  a name for a repo [default: ]
    -u, --repo-url   where is the upstream git repo [default: git@github.com:dreamboxlearning/chef-environments.git]
    -n, --dry-run    a boolean flag that tells what will happen, but not actually execute it [default: True]
    '''
    try:
        arguments = docopt.docopt(clone_env_apps.__doc__, argv=argv, options_first=True)
        args = arguments['<args>']
        fromEnv = args[0]
        toEnv = args[1]
        (fromEnv, toEnv) = args[1:]
        print('clone from: %s to %s' % (fromEnv, toEnv))
    except docopt.DocoptExit as docoptExit:
        print(docoptExit.message, file=sys.stderr)
    except Exception as exception:
        print(exception.message, file=sys.stderr)
