#!/usr/bin/env python

import os, re, pathlib
from tempfile import mkstemp
from shutil import move, copymode
from os import fdopen, remove

def bump_version_number(repo, files, options):
    # If repo is valid, get the most recent commit hash
    # short_hash = repo.git.rev_parse('HEAD', short=True)
    if options.git_user_name != None:
        git_username = options.git_user_name
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
        build_num = write_version_file(f, version_num_pattern)
        repo.git.add(f)

    repo.git.config(['user.name', [git_username]])    
    repo.git.config(['user.email', [git_useremail]])    
    repo.git.commit('-m',
                     '[git-version-bump]\nBuild Number: ' 
                        + build_num)
    repo.create_tag(''.join(['v',build_num]), message=f'Automatic tag \"v{build_num}\"')

def write_version_file(file_path, regex_pattern):
    """Bumps up the build version number of the specified file"""
    
    new_version_num = ''

    #Create temp file
    fh, abs_path = mkstemp()
    with fdopen(fh, 'w') as new_file:
        with open(file_path) as old_file:
            for i, line in enumerate(old_file):
                
                matches = re.finditer(regex_pattern, line)
                if not is_valid_version(file_path, line):
                    new_file.write(line)
                    continue

                for match in matches:
                        prev_ver_num = match.group()
                        version_num = prev_ver_num.split('.')
                        build_num = int(version_num[-1])
                        build_num += 1

                        new_version_num = ''
                        for num in version_num[:-1]:
                            new_version_num = ''.join([new_version_num, str(num), '.'])
                        
                        new_version_num = ''.join([new_version_num, str(build_num)])
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
