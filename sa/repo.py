#!/usr/bin/env python

import os, git

# push code from an https cloned repo
def push(repo, username, password):

    for remote in repo.remotes:
        index = remote.url.find('//') + 2
        new_url = remote.url[:index] + f'{username}:{password}@' + remote.url[index:]
        remote.set_url(new_url)

    os.environ['GIT_USERNAME'] = username
    os.environ['GIT_PASSWORD'] = password
    for remote in repo.remotes:
        remote.push()
        remote.push(['--tag'])

def reattach_head(repo):
    head_info = repo.git.show(['-s', '--pretty=%d', 'HEAD'])
    for branch in repo.refs:
        branch = str(branch).replace('origin/','')
        if branch in head_info:
            repo.git.checkout(branch)
            break

def is_git_repo(path):
    """Returns if a given path is a git repo"""

    try:
        _ = git.Repo(path).git_dir
        return True
    except Exception:
        return False

def get_changed_files(repo):
    """return a list of all of the changed files based on the last commit"""
    if repo != None:
        return list(repo.commit(repo.head.object.hexsha).stats.files.keys())
    return []
