from __future__ import print_function
import dreambox.git.client as Git
import dreambox.utils
import dreambox.json.chef_env as chef_env
import os
import sys

from dreambox.json.chef_env import update_environments

def __merge_updated_chef_environment_file(from_env='production.json',
                                          to_env='stage1',
                                          repo_path='/tmp',
                                          repo_name='chef-environments',
                                          repo_url='git@github.com:wilddog64/chef-environments.git',
                                          sync_cookbook_version=True,
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
* sync_cookbook_version is a flag that tells if function should sync two environments.  Default
  is True.  Set to False if you don't want to sync two environments' cookbook versions
    '''
    currentUser = dreambox.utils.get_current_user()
    currentTimestamp = dreambox.utils.current_timestamp()
    appPath = repo_path
    if repo_name is not None:
        appPath = os.path.join(repo_path, repo_name)

    envFilePath = os.path.join(appPath, from_env)
    Git.clone_repo_to_local(git_url=repo_url,
                            repo_path=repo_path,
                            app_name=repo_name,
                            recurse_submodules=False,
                            force_remove_repo=True)
    branchName = 'merge-production-to-stage'
    Git.create_branch(branch_name=branchName,
                      repo_path=appPath,
                      create_and_switch=True)
    to_list = []
    if ',' in to_env:
        to_list = to_env.split(',')
    else:
        to_list = [to_env]

    commitMessage = 'automic update %s base on %s by %s at %s' % (','.join(to_list),
                                                                  from_env,
                                                                  currentUser,
                                                                  currentTimestamp)
    mergeMessage = 'merge branch %s to master via automation process' % branchName
    update_environments(from_file=envFilePath, to=to_list)
    if sync_cookbook_version:
        for env in to_list:
            chef_env.update_chef_environment_cookbooks(sourceEnvFile=envFilePath,
                                                       targetEnvFile=env,
                                                       repo=repo_url,
                                                       repoName=repo_name,
                                                       workspace=repo_path)
    else:
        print('sync_cookbook_version is set to false, no cookbook versions synced')

    if Git.repo_is_dirty(repo=appPath):
        Git.commit(repoPath=appPath, commitMessage=commitMessage)
        Git.merge_branch(repo_path=appPath,
                         from_branch=branchName,
                         to_branch='master',
                         merge_message=mergeMessage)
        Git.push_ref(repo_path=appPath,
                     dry_run=dry_run)
    else:
        print('nothing changes, no push')


def clone_env_apps(args=None):
    from_env = args.from_env
    to_env = args.to_env
    repo_path = args.repo_path
    repo_name = args.repo_name
    repo_url = args.repo_url
    dry_run = dreambox.utils.to_bool(args.dry_run)
    sync_cookbook_version = dreambox.utils.to_bool(args.sync_cookbook_version)

    message = '''
clone from %s to %s --repo-path %s --repo-name %s --repo-url %s --dry-run %s
    ''' % (from_env, to_env, repo_path, repo_name, repo_url, dry_run)

    print(message, file=sys.stderr)

    __merge_updated_chef_environment_file(from_env,
                                          to_env,
                                          repo_path,
                                          repo_name,
                                          repo_url,
                                          sync_cookbook_version,
                                          dry_run)


def diff_env_cookbook_pinned_versions(args=None):
    sourceEnv = args.source
    targetEnv = args.target
    repo=args.repo
    repoName=args.repo_name
    workspace=args.workspace

    if repoName is None:
        repoName = 'chef-environment'
    print('source environment %s' % sourceEnv)
    print('target environment %s' % targetEnv)
    print('repo url %s' % repo)
    print('repo name %s' % repoName)
    print('workspace %s' % workspace)

    repoPath = os.path.join(workspace, repoName)
    if not os.path.exists(repoPath):
        print('repo exists at %s' % repoPath)
        Git.clone_repo_to_local(git_url=repo,
                                repo_path=workspace,
                                app_name=repoName,
                                recurse_submodules=False,
                                force_remove_repo=True)
    elif Git.project_isa_gitrepo(project_path=repoPath):
        Git.pull(repoPath)

    (missingCookbooks,
     mismatchCookbookVersions,
     source,
     target,
     sourcePath,
     targetPath) = chef_env.compare_env_cookbook_versions(source=sourceEnv,
                                                          target=targetEnv,
                                                          repo=repo,
                                                          repoName=repoName,
                                                          workspace=workspace)
    if missingCookbooks:
        dreambox.utils.print_structure(missingCookbooks)
    else:
        print('no missing cookbooks found')

    if mismatchCookbookVersions:
        print('--- mismatch cookbook versions ---', file=sys.stderr)
        dreambox.utils.print_structure(mismatchCookbookVersions)
        for key in mismatchCookbookVersions:
            print('%s has cookbook %s version %s' % (sourcePath, key, source['cookbook_versions'][key]), file=sys.stderr)
            print('%s has cookbook %s version %s' % (targetPath, key, target['cookbook_versions'][key]), file=sys.stderr)



if __name__ == '__main__':
    (missingCookbooks,
     mismatchCookbookVersions,
     source,
     target,
     sourcePath,
     targetPath) = chef_env.compare_env_cookbook_versions(target='stage1.json')

    sourceEnvFile = '/tmp/chef-environments/production.json'
    targetEnvFile = '/tmp/chef-environments/stage1.json'
    repo='git@github.com:wilddog64/chef-environments.git'
    repoName = 'chef-environments'
    chef_env.update_chef_environment_cookbooks(sourceEnvFile=sourceEnvFile,
                                               targetEnvFile=targetEnvFile,
                                               repo='git@github.com:dreamboxlearning/chef-environments.git',
                                      repoName=repoName)
