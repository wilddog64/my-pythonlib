from __future__ import print_function
import dreambox.git.core as Git
import os
import shutil
import sys


def __output_callback(line):
    '''
a internall callback function that can be hooked up
to sh package to catpure and process program output
    '''
    print(line.rstrip("\n"))


def initialize_repo(repo_path='.', repo_name=None):
    '''
initialize_repo is a function that perform a git init to create
a git repo.  The function takes two parameters,

* repo_path is a path to the repo to be created.  If not provide, assume
current directory.
* repo_name is the name of a repo to created. It is a required parameter.
    '''
    return Git.init(repo=repo_name, _cwd=repo_path)


def clone_repo_to_local(git_url=None,
                        repo_path=None,
                        app_name=None,
                        stderr_callback=__output_callback,
                        stdout_callback=__output_callback,
                        recurse_submodules=False,
                        force_remove_repo=False):
    '''
clone_repo_to_local is a function that will clone a remote repo into a local path.
The function takes the following parameters,

* git_url is an remote url that has a valid git repo.  This can be either ssh or https

* repo_path is a local repo path that clone one stored

* app_name is a name of the repo at local

* stderr_callback is a function reference that will assign to stderr callback
  (details in sh README.md).  This assigned to __output_callback by default

* stdout_callback is a function reference that will assign to stderr callback
  (details in sh README.md)  This assigned to __output_callback by default

* recurse_submodules is a boolean flag that tells git clone to recursively bring down all
  the submodules.  Default value is False

* force_remove_repo is a boolean flag that tell clone_repo_to_local to remove existing repo
  before clone it from remote.  By default, this is set to false

Note: if local repo already exist, unless force_remove_repo is set to true, it will pull
      from remote repo.
    '''
    app_path = os.path.join(repo_path, app_name)
    print('working on %s' % app_path, file=sys.stderr)

    # if repo exists and for_remove_repo flag is on, or
    # repo does not exists then we will clone it from remote;
    # otherwise, we do git pull
    clone_repo = False
    if os.path.exists(app_path) and force_remove_repo:
        shutil.rmtree(app_path)
        clone_repo = True
    elif not os.path.exists(app_path):
        clone_repo = True
    else:
        if get_current_branch_name(repo_path=app_path) != 'master':
          Git.checkout('master', _cwd=app_path)
        Git.pull(_cwd=app_path)

    # we only clone repo if clone_repo flag is set to true
    if clone_repo: 
        Git.clone(git_url,
                  app_name,
                  _cwd=repo_path,
                  recurse_submodules=recurse_submodules,
                  _err=stderr_callback,
                  _out=stderr_callback)



def create_branch(branch_name=None,
                  repo_path=None,
                  stderr_callback=__output_callback,
                  stdout_callback=__output_callback,
                  create_and_switch=False,):
    '''
create_branch function will create a branch in a given repo.  The function
takes the following parameters,

* branch_name is a name of a branch to be created

* repo_path a path points to a git repo where a branch should create

* stderr_callback is a function reference that will assign to stderr callback
  (details in sh README.md).  This assigned to __output_callback by default

* stdout_callback is a function reference that will assign to stderr callback
  (details in sh README.md)  This assigned to __output_callback by default

* create_and_switch is a boolean flag that tells create_branch once branch created,
  switch to it.  This is set to true by default.
    '''
    if create_and_switch:
       if not branch_exists(branch_name=branch_name,
                            repo_path=repo_path):
           Git.checkout(branch_name,
                        _cwd=repo_path,
                        b=create_and_switch,
                        _err=stderr_callback,
                        _out=stdout_callback)
       elif get_current_branch_name(repo_path=repo_path) != branch_name:
           print('branch %s already exists, switch to it' % branch_name)
           Git.checkout(branch_name,
                        _cwd=repo_path,
                        _err=stderr_callback,
                        _out=stdout_callback)
    else:
       Git.branch(branch_name,
                  _cwd=repo_path,
                  _err=stderr_callback,
                  _out=stdout_callback)


def remove_repo_untrack_files(repo_path, dry_run=False):
    '''
remove_repo_untrack_files function will remove all the untrack files and recitories
for a given git repo.  The function takes the following parameters,

* repo_path is a full path points to a given repo.

* dry_run is a boolean flag to indicate not to take action to remove files but show what
  is going to happen.  This is set to False by default.
    '''
    if dry_run:
        return Git.clean(_cwd=repo_path, d=True, f=True, x=True, n=True, _out=__output_callback)
    else:
        return Git.clean(_cwd=repo_path, d=True, f=True, x=True, _out=__output_callback)


def get_current_branch_name(repo_path='.',
                            stderr_callback=__output_callback,
                            stdout_callback=__output_callback,
                          ):
    '''
get_current_branch_name will return the name of currently use branch.  The
function takes the following parameters,

* repo_path is a path points to a git repo

* stderr_callback is a function reference that will assign to stderr callback
  (details in sh README.md).  This assigned to __output_callback by default

* stdout_callback is a function reference that will assign to stderr callback
  (details in sh README.md)  This assigned to __output_callback by default

    '''
    return Git.symbolic_ref('HEAD',
                            short=True,
                            q=True,
                            _cwd=repo_path,
                            _out=stdout_callback,
                            _err=stderr_callback)


def merge_branch(repo_path='.',
                 from_branch=None,
                 to_branch=None,
                 merge_message='auto-merge from script',
                 stderr_callback=__output_callback,
                 stdout_callback=__output_callback):
    '''
merge_branch function merge branches from A to B.  The function takes the
following parameters,

* repo_path is a full path points to a git repo to work on

* from_branch is a branch that is going to be merged

* to_branch is a branch that takes a branch to merge in.

* merge_message is a merge commit message.

* stderr_callback is a function reference that will assign to stderr callback
  (details in sh README.md).  This assigned to __output_callback by default

* stdout_callback is a function reference that will assign to stderr callback
  (details in sh README.md)  This assigned to __output_callback by default

note: merge_branch only perform a simple no fast forward merge
    '''
    current_branch = get_current_branch_name(repo_path=repo_path)
    if current_branch != to_branch:
        Git.checkout(to_branch,
                     _cwd=repo_path,
                     _err=stderr_callback,
                     _out=stdout_callback)
    Git.merge(from_branch,
              no_ff=True,
              m=merge_message,
              _cwd=repo_path,
              _err=stderr_callback,
              _out=stdout_callback)


def push_ref(repo_path='.',
             remote='origin',
             ref=None,
             set_upstream=False,
             dry_run=False,
             stderr_callback=__output_callback,
             stdout_callback=__output_callback,
             ):
    '''
push_ref will update remote references with local one.  The function
takes the following parameters,

* repo_path is a path points to a repo to push references.  Default
  value is current directory ".".
* remote is a remote repo.  This normally is origin or it can be
  different remote name defined in .git/config
* ref is a reference to push, the can be a master or a local branch
* set_upstream is a boolean flag that tells 'git push' to setup tracking
  upstream.  So after first push, you can simply do

      git push

  rather than

      git push origin <ref>
* dry_run is a boolean flag that when set to true, will do everything except
  send an update to remote.

* stderr_callback is a function reference that will assign to stderr callback
  (details in sh README.md).  This assigned to __output_callback by default

* stdout_callback is a function reference that will assign to stderr callback
  (details in sh README.md)  This assigned to __output_callback by default


    '''
    if ref is None:
        Git.push(n=dry_run,
                 u=set_upstream,
                 _cwd=repo_path,
                 _err=__output_callback)
    else:
        Git.push(remote,
                 ref,
                 n=dry_run,
                 u=set_upstream,
                 _cwd=repo_path,
                 _err=stderr_callback,
                 _out=stdout_callback)


def commit(repoPath=None,
           add=True,
           commitMessage=None,
           stderr_callback=__output_callback,
           stdout_callback=__output_callback):
    Git.commit(a=add,
               m=commitMessage,
               _cwd=repoPath,
               _err=stderr_callback,
               _out=stdout_callback)


def branch_exists(branch_name=None, repo_path='.'):
    '''
branch_exists function will check to see if a given git
branch exists in current repo or not. The function takes the
following parameters

* branch_name is a git branch to check
* repo_name is where repo that contains a branch_name
    '''
    rc = Git.rev_parse(branch_name,
                       _cwd=repo_path,
                       quiet=True,
                       verify=True,
                       _ok_code=[0, 1])
    return not rc


def pull(repoPath='.'):
    Git.pull(_cwd=repoPath)


def project_isa_gitrepo(project_path='.'):
    '''
project_isa_gitrepo is a function to verify if a given project (directory)
is actually a git repo or not.  The function takes only one parameter,

* project_path is a path to project that this function is trying to verify
    '''
    rc = Git.rev_parse(_cwd=project_path,
                       is_inside_work_tree=True,
                       quiet=True,
                       _ok_code=[0, 128])

    return not rc

def repo_is_dirty(repo='.'):
    '''
repo_is_dirty is a function to check if current repo has unstaged changes.
The function takes only one parameter,

* repo is a full path points to a git repo to check
    '''
    return Git.diff_files(_cwd=repo, quiet=True, _ok_code=[0, 1])

if __name__ == '__main__':
    repoPath = '/tmp'
    repoName = 'git-testing'
    initialize_repo(repo_path=repoPath, repo_name=repoName)
    print('checking if %s is actually a git repo', file=sys.stderr)
    if project_isa_gitrepo(project_path=os.path.join(repoPath, repoName)):
      print('%s is a valid git repo' % repoName)

    repoUrl = 'git@github.com:dreamboxlearning/chef-environments.git'
    appName = 'environments'
    appPath = os.path.join(repoPath, appName)

    print('testing clone_repo_to_local', file=sys.stderr)
    clone_repo_to_local(git_url=repoUrl,
                        repo_path=repoPath,
                        app_name=appName,
                        force_remove_repo=False)
    print('end testing clone_repo_to_local', file=sys.stderr)
    Git.checkout('master', _cwd=appPath)
    print()
    print('testing create_branch')
    create_branch(branch_name='production',
                  repo_path=appPath,
                  stderr_callback=__output_callback,
                  stdout_callback=__output_callback,
                  create_and_switch=True,)
    print('end testing create_branch')
    print()
    print('testing remove_repo_untrack_files with dry_run set to true')
    remove_repo_untrack_files(repo_path='.', dry_run=True)
    print('end testing remove_repo_untrack_files with dry_run set to true')
    print()
    print('testing get_current_branch_name')
    get_current_branch_name()
    print('end testing get_current_branch_name')
    print()
    print('testing push_ref with -n (dry_run)')
    push_ref(dry_run=True)
    print('end testing push_ref with -n (dry_run)')
    print()
