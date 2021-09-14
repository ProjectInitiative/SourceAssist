#!/usr/bin/env python

from devops._version import __version__
import sys, os, argparse, git
from devops.versioning import bump_version_number
from devops.repo import push_git_repo, is_git_repo, reattach_head

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

    # gitpush
    parser_gitpush = subparsers.add_parser('gitpush')
    add_required_creds_args(parser_gitpush)
    add_required_repo_args(parser_gitpush)

    # bumpversion
    parser_bumpversion = subparsers.add_parser('bumpversion')
    add_required_repo_args(parser_bumpversion)
    parser_bumpversion.add_argument(
                    dest='files', 
                    type=str, 
                    nargs='*',
                    help='list all files to be updated with new version number')
    # TODO add flag to allow for custom provided versioning script
    
    # checkprevcommit
    parser_checkprevcommit = subparsers.add_parser('checkprevcommit')
    add_required_repo_args(parser_checkprevcommit)



    # Process CLI arguments
    options = parser.parse_args()

    if options.command == 'gitpush':
        push_git_repo(get_git_repo(options.repo_dir), options.username, options.password)
        exit()
    
    elif options.command == 'bumpversion':
        # Process all file paths provided and only include the valid files 
        bump_version_number(get_git_repo(options.repo_dir), options.files, options)
        exit()
    
    elif options.command == 'checkprevcommit':
        pass
        # check_prev_commit(get_git_repo(options.repo_dir))

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