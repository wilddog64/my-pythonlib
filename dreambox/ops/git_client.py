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
    appPath = repo_path
    if repo_name is not None:
        appPath = os.path.join(repo_path, repo_name)

    envFilePath = os.path.join(appPath, from_env)
    Git.clone_repo_to_local(git_url=repo_url,
                            repo_path=repo_path,
                            app_name=repo_name,
                            recurse_submodules=False,
                            force_remove_repo=True)
    branchName = 'merge-production-to-stage_env-by_%s@%s' % (currentUser, currentTimestamp)
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
    Git.commit(repoPath=appPath, commitMessage=commitMessage)

    Git.merge_branch(repo_path=appPath,
                     from_branch=branchName,
                     to_branch='master',
                     merge_message=mergeMessage)
    Git.push_ref(repo_path=appPath,
                 dry_run=dry_run)


def clone_env_apps(args=None):
    from_env = args.from_env
    to_env = args.to_env
    repo_path = args.repo_path
    repo_name = args.repo_name
    repo_url = args.repo_url
    dry_run = args.dry_run
    message = '''
clone from %s to %s --repo-path %s --repo-name %s --repo-url %s --dry-run %s
    ''' % (from_env, to_env, repo_path, repo_name, repo_url, dry_run)

    print(message, file=sys.stderr)

    __merge_updated_chef_environment_file(args.from_env,
                                          args.to_env,
                                          args.repo_path,
                                          args.repo_name,
                                          args.repo_url,
                                          args.dry_run)


def compare_env_cookbook_versions(source='production.json',
                                  target='stage1.json',
                                  repo='git@github.com:dreamboxlearning/chef-environments.git',
                                  repoName='chef-environments',
                                  workspace='/tmp'):
    '''
compare_env_cookbook_versions function compare cookbook versions pin in two environments and
report the difference between them.  The function takes the following parameters,

* source is a source chef environment file
* target is a target chef environment file to compare with source
* repo is a git repository url
* workspace is where git repository will be cloned to
    '''
    Git.clone_repo_to_local(git_url=repo,
                            repo_path=workspace,
                            app_name=repoName,
                            recurse_submodules=False,
                            force_remove_repo=False)
    fullPath = os.path.join(workspace, repoName)
    sourcePath = os.path.join(fullPath, source)
    targetPath = os.path.join(fullPath, target)
    sourceCookbookJson, sourceDir, sourceFilename = chef_env.load_chef_environment_attributes(sourcePath, 'cookbook_versions')
    targetCookbookJson, targetDir, targetFilename = chef_env.load_chef_environment_attributes(targetPath, 'cookbook_versions')
    mismatch_key, delta = chef_env.get_delta_set(sourceCookbookJson, targetCookbookJson)

    sourceObject = chef_env.load_chef_environment_file(sourcePath)
    targetObject = chef_env.load_chef_environment_file(targetPath)

    return mismatch_key, delta, sourceObject, targetObject, sourcePath, targetPath


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
    (missingCookbooks,
     mismatchCookbookVersions,
     source,
     target,
     sourcePath,
     targetPath) = compare_env_cookbook_versions(source=sourceEnv,
                                                 target=targetEnv,
                                                 repo=repo,
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
            target['cookbook_versions'][key] = source['cookbook_versions'][key]


if __name__ == '__main__':
    import json
    (missingCookbooks,
     mismatchCookbookVersions,
     source,
     target,
     sourcePath,
     targetPath) = compare_env_cookbook_versions(target='stage1.json')

    if missingCookbooks:
        dreambox.utils.print_structure(missingCookbooks)
    else:
        print('no difference found')

    if mismatchCookbookVersions:
        print('found values of element are different')
        print('--- list different ---')
        print('total elements need to update: %s' % len(mismatchCookbookVersions), file=sys.stderr)
        print('--- mismatch cookbook versions ---', file=sys.stderr)
        dreambox.utils.print_structure(mismatchCookbookVersions)
        for key in mismatchCookbookVersions:
            print('%s has cookbook %s version %s' % (sourcePath, key, source['cookbook_versions'][key]), file=sys.stderr)
            print('%s has cookbook %s version %s' % (targetPath, key, target['cookbook_versions'][key]), file=sys.stderr)
            print('updating mismatch cookbook versions now ...', file=sys.stderr)
            target['cookbook_versions'][key] = source['cookbook_versions'][key]
        with open(targetPath, 'w') as updateh:
            updateh.write(json.dumps(target, sort_keys=True, indent=2, separators=(',', ': ')))
