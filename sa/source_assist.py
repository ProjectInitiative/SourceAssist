#!/usr/bin/env python

import sys
# add current directory to path
sys.path.insert(0, '')

from sa import _version, repo as rp, versioning, docker_api
import os, argparse, git

def main():
    # initialize argparser
    parser = argparse.ArgumentParser()
    # initialize sub argument parsers
    subparsers = parser.add_subparsers(dest='command')

    parser.add_argument('--version', action='version',
                    version='%(prog)s {version}'.format(version=_version.__version__))

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
    git_subparser_push = subparser_git.add_parser('push')
    add_required_creds_args(git_subparser_push)
    add_required_repo_args(git_subparser_push)
    # git checkprevcommit
    git_subparser_checkprevcommit = subparsers.add_parser('checkprevcommit')
    add_required_repo_args(git_subparser_checkprevcommit)


    # version
    parser_version = subparsers.add_parser('version')
    subparser_version = parser_version.add_subparsers(dest='version_subcommand')
    # version get
    version_subparser_get = subparser_version.add_parser('get')
    add_optional_docker_arg(version_subparser_get)
    add_required_files_args(version_subparser_get)
    # version bump
    version_subparser_bump = subparser_version.add_parser('bump')
    add_required_repo_args(version_subparser_bump)
    add_optional_docker_arg(version_subparser_bump)
    add_required_files_args(version_subparser_bump)
    # TODO add flag to allow for custom provided versioning script


    # docker
    parser_docker = subparsers.add_parser('docker')
    subparser_docker = parser_docker.add_subparsers(dest='docker_subcommand')
    # docker build
    docker_subparser_build = subparser_docker.add_parser('build')
    add_required_files_args(docker_subparser_build)
    # docker geninfo
    #TODO: generate sample docker info json file


    # Process CLI arguments
    options = parser.parse_args()

    if options.command == 'git':

        if options.git_subcommand == 'push':
            rp.push(get_git_repo(options.repo_dir), options.username, options.password)
            exit()
        elif options.git_subcommand == 'checkprevcommit':
            #TODO: implement function
            rp.check_prev_commit(get_git_repo(options.repo_dir))

    elif options.command == 'version':

        if options.version_subcommand == 'bump':
            # Process all file paths provided and only include the valid files 
            rp.version_bump(get_git_repo(options.repo_dir), get_files(options.files), options)
            exit()
        elif options.version_subcommand == 'get':
            # Process all files paths provided and only include the valid files
            version_info = versioning.version_get(get_files(options.files), options)
            for file,version in version_info:
                print(''.join([file,' ', version]))
            exit()

    elif options.command == 'docker':

        if options.docker_subcommand == 'build':
            docker_api.build(get_files(options.files))
        elif options.docker_subcommand == 'push':
            docker_api.push()


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
    if (rp.is_git_repo(abs_repo_path)):
        repo = git.Repo(abs_repo_path)
        rp.reattach_head(repo)
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
        print('no files provided, use \'-h|--help\' for more details'.format())
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