#!/usr/bin/env python

import sys
# add current directory to path
sys.path.insert(0, '')

from devops._version import __version__
import os, argparse, git
from devops.versioning import version_bump, check_prev_commit
from devops.repo import git_push_repo, is_git_repo, reattach_head

def main():
    # initialize argparser
    parser = argparse.ArgumentParser()
    # initialize sub argument parsers
    subparsers = parser.add_subparsers(dest='command')

    parser.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format(version=__version__))

    parser.add_argument('-gu','--gitusername',
                    dest='git_username',
                    type=str,
                    help='git username to use during commits, defaults to \'Jenkins\'')
    parser.add_argument('-ge','--gituseremail',
                    dest='git_useremail',
                    type=str,
                    help='git email to use during commits, defaults to \'jenkins@noreply.com\'')

    # git
    parser_git = subparsers.add_parser('git')
    subparser_git = parser_git.add_subparsers(dest='git_subcommand')
    # git push 
    subparser_push = subparser_git.add_parser('push')
    add_required_creds_args(subparser_push)
    add_required_repo_args(subparser_push)
    # git checkprevcommit
    subparser_checkprevcommit = subparsers.add_parser('checkprevcommit')
    add_required_repo_args(subparser_checkprevcommit)


    # version
    parser_version = subparsers.add_parser('version')
    subparser_version = parser_version.add_subparsers(dest='version_subcommand')
    # version get
    subparser_get = subparser_version.add_parser('get')
    add_optional_docker_arg(subparser_get)
    add_required_files_args(subparser_get)
    # version bump
    subparser_bump = subparser_version.add_parser('bump')
    add_required_repo_args(subparser_bump)
    add_optional_docker_arg(subparser_bump)
    add_required_files_args(subparser_bump)
    # TODO add flag to allow for custom provided versioning script


    # Process CLI arguments
    options = parser.parse_args()

    if options.command == 'git':
        if options.git_subcommand == 'push':
            git_push_repo(get_git_repo(options.repo_dir), options.username, options.password)
            exit()
        elif options.git_subcommand == 'checkprevcommit':
            #TODO: implement function
            check_prev_commit(get_git_repo(options.repo_dir))
    
    elif options.command == 'version':
        if options.version_subcommand == 'bump':
            # Process all file paths provided and only include the valid files 
            version_bump(get_git_repo(options.repo_dir), get_files(options.files), options)
            exit()
        elif options.version_subcommand == 'get':
            # Process all files paths provided and only include the valid files
            version_get(get_files(options.files), options)
            exit()


def get_git_repo(repo_dir):
    # get/validate absolute path of provided repository directory
    abs_repo_path = ""
    if repo_dir != None:
        if os.path.isdir(repo_dir):
            abs_repo_path = os.path.abspath(repo_dir)
        else:
            # raise argparse.ArgumentTypeError(f"readable_dir:{repo_dir} is not a valid path")
            print(f'readable_dir:{abs_repo_path} is not a valid path')
            exit(1)
    
    # validate provided path is a git repository and setup for use 
    if (is_git_repo(abs_repo_path)):
        repo = git.Repo(abs_repo_path)
        reattach_head(repo)
    else:
        # raise Exception(f"{repo_dir} is not a valid git repository")
        print(f'{abs_repo_path} is not a valid git repository')
        exit(1)
    return repo

def get_files(infiles):
    files = []
    if infiles != None:
        for f in infiles:
            if os.path.isfile(f):
                files.append(os.path.abspath(f))
    
    if (len(files) == 0):
        print('no files provided, use \'devops -h\' for more details')
        exit(1)
    return files

def add_required_files_args(parser):
    parser.add_argument(
                    dest='files', 
                    type=str, 
                    nargs='*',
                    help='list of all files to be to be operated on')

def add_optional_docker_arg(parser):
    parser.add_argument('-d','--docker',
                    action='store_true',
                    help='indicate if provided files are docker-info.json files for versioning')

def add_required_creds_args(parser):
    parser.add_argument('-u','--username',
                    dest='username',
                    required=True,
                    help='username for logging into service')
    parser.add_argument('-p','--password',
                    dest='password',
                    required=True,
                    help='password for logging into service')

def add_required_repo_args(parser):
    parser.add_argument('-r','--repo',
                    dest='repo_dir',
                    type=str,
                    required=True,
                    help='specific path to git project files')

if __name__ == '__main__':
    sys.exit(main())