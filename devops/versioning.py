#!/usr/bin/env python

from devops.repo import get_changed_files
import os, re, pathlib, json
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

def check_prev_commit(repo, custom_tags):
    """Check to make sure the previous commit is not an automated on or contains specific tags"""
    return None

def version_bump(repo, files, options):
    # If repo is valid, get the most recent commit hash
    # short_hash = repo.git.rev_parse('HEAD', short=True)
    if options.git_username != None:
        git_username = options.git_username
    else:
        git_username = 'Jenkins'
    if options.git_useremail != None:
        git_useremail = options.git_useremail
    else:
        git_useremail = 'jenkins@noreply.com'


    # Regex pattern to match all version numbers
    version_num_pattern = re.compile('(\\d*\\d?\\.\\d*\\d)+')
    build_num = ''
    for f in files:
        build_num = write_version_file(f, version_num_pattern, repo=repo, options=options)
        repo.git.add(f)

    repo.git.config(['user.name', [git_username]])    
    repo.git.config(['user.email', [git_useremail]])    
    repo.git.commit('-m',
                     '[git-version-bump]')
    #TODO: fix multi-build number issues
    # repo.git.commit('-m',
    #                  '[git-version-bump]\nBuild Number: ' 
    #                     + build_num)
    # repo.create_tag(''.join(['v',build_num]), message=f'Automatic tag \"v{build_num}\"')

def update_version(prev_ver_num):
    version_num = prev_ver_num.split('.')
    build_num = int(version_num[-1])
    build_num += 1

    new_version_num = ''
    for num in version_num[:-1]:
        new_version_num = ''.join([new_version_num, str(num), '.'])
    
    new_version_num = ''.join([new_version_num, str(build_num)])
    return new_version_num

def search_json_dict(dict_obj, file_names, version_data = [], write=False):

    if isinstance(dict_obj, list):
        for obj in dict_obj:
            search_json_dict(obj, file_names)
    elif isinstance(dict_obj, dict):
        # check if all keys are in dictionary
        if not(['version','file'] - dict_obj.keys()):
            # only update version number for files that have been modified
            if any([dict_obj['file'].lower() in file_name.lower() for file_name in file_names]):
                print(f'Found on changes in: {dict_obj["file"]} {dict_obj["version"]}')
                # update version number if specified
                if write:
                    dict_obj['version'] = update_version(dict_obj['version'])
                    print(f'Updated to: {dict_obj["file"]} {dict_obj["version"]}')
                return (dict_obj['file'], dict_obj['version'])
        # check for a nested dictionary or list of dictionaries
        else:
            for k,v in dict_obj.items():
                if isinstance(v, (dict, list)):
                    search_json_dict(v, file_names)

def write_version_file(file_path, regex_pattern, **kwargs):
    """Bumps up the build version number of the specified file"""

    #Create temp file
    fh, abs_path = mkstemp()
    new_version_num = ''


    with fdopen(fh, 'w') as new_file:
        with open(file_path, 'r') as old_file:

            # check if JSON, and if the file is a docker versioning JSON
            if file_path.endswith('.json'):
                if 'options' in kwargs and 'repo' in kwargs:
                    repo = kwargs.get('repo')
                    options = kwargs.get('options')
                    if 'docker' in options and options.docker:
                        changed_files = get_changed_files(repo)
                        docker_info = json.load(old_file)
                        search_json_dict(docker_info, [str(path) for path in changed_files])
                        # search_json_dict(docker_info, changed_files)
                        json.dump(docker_info, new_file, indent=4)

            else:
                for i, line in enumerate(old_file):
                    
                    matches = re.finditer(regex_pattern, line)
                    if not is_valid_version(file_path, line):
                        new_file.write(line)
                        continue

                    for match in matches:
                            prev_ver_num = match.group()
                            new_version_num = update_version(prev_ver_num)
                            new_line = line.replace(prev_ver_num, new_version_num)
                            new_file.write(new_line)

                            print(f'Found on line {i+1}: {prev_ver_num}')
                            print(f'Changed {line.strip()} to {new_line.strip()}')
                    
    #Copy the file permissions from the old file to the new file
    copymode(file_path, abs_path)
    #Remove original file
    remove(file_path)
    #Move new file
    move(abs_path, file_path)
    
    return new_version_num



def is_valid_version(file_path, line):
    """Returns if the specified line that contains a version number
       is the valid one for that file type"""

    file_name = os.path.basename(file_path)
    ext = pathlib.Path(file_path).suffix
    if ext != '':
        if ext == '.py':
            if '__version__' in line:
                return True
        
        if ext == '.json':
            if 'version' in line:
                return True
        
        if ext == '.csproj':
            if '</Version>' in line:
                return True
        
        if ext == '.cs':
            if 'AssemblyVersion' in line or 'AssemblyFileVersion' in line:
                return True
    else:
        if file_name == 'Doxyfile':
            if 'PROJECT_NUMBER' in line:
                return True
    
    return False
