#!/usr/bin/env python

from sa import utils, repo as rp
import os, re, pathlib, json
import tempfile
import shutil
def check_prev_commit(repo, custom_tags):
    """Check to make sure the previous commit is not an automated on or contains specific tags"""
    return None

def version_get(files, options):

    build_info = []
    # Regex pattern to match all version numbers
    version_num_pattern = re.compile('(\\d*\\d?\\.\\d*\\d)+')
    for f in files:
        build_info = build_info + parse_version_file(f, version_num_pattern, options=options)
    return build_info

def version_bump(repo, files, options):
    # If repo is valid, get the most recent commit hash
    # short_hash = repo.git.rev_parse('HEAD', short=True)
    if options.git_username != None:
        git_username = options.git_username
    else:
        git_username = 'SourceAssist'
    if options.git_useremail != None:
        git_useremail = options.git_useremail
    else:
        git_useremail = 'SourceAssist@noreply.com'


    # Regex pattern to match all version numbers
    version_num_pattern = re.compile('(\\d*\\d?\\.\\d*\\d)+')
    build_info_string = '[git-version-bump]'
    for f in files:
        build_info = parse_version_file(f, version_num_pattern, write=True, repo=repo, options=options)
        for file, version in build_info:
            build_info_string = ''.join([build_info_string,'\n', file, ' ', version])
        repo.git.add(f)


    repo.git.config(['user.name', [git_username]])    
    repo.git.config(['user.email', [git_useremail]])    
    repo.git.commit('-m', build_info_string)
    #TODO: fix multi-build number issues
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

def version_data_from_dict(dict_obj, keys, file_names, write=False):

    version_data = []
    found_dicts = utils.find_key_pairs(dict_obj, keys)

    for found_dict in found_dicts:

        # only update version number for files that have been modified
        if any([found_dict['file'].lower() in file_name.lower() for file_name in file_names]):
            print(f'Found on changes in: {found_dict["file"]} {found_dict["version"]}')
            # update version number if specified
            found_dict['version'] = update_version(found_dict['version'])
            print(f'Updated to: {found_dict["file"]} {found_dict["version"]}')
            # write and return only updated version numbers
            version_data.append((found_dict['file'], found_dict['version']))
        
        elif not write:
            # return all version data found
            version_data.append((found_dict['file'], found_dict['version']))
        
    return version_data

def parse_version_file(file_path, regex_pattern, write=False, **kwargs):
    """Bumps up the build version number of the specified file"""

    options = None
    repo = None
    if 'options' in kwargs:
        options = kwargs.get('options')
    if 'repo' in kwargs:
        repo = kwargs.get('repo')

    version_info = []
    new_version_num = ''
    new_file = None

    with open(file_path, 'r') as old_file:
        if write:
            #Create temp file
            fh, abs_path = tempfile.mkstemp()
            new_file = os.fdopen(fh, 'w')

        # check if JSON, and if the file is a docker versioning JSON
        if options != None and 'docker' in options and options.docker:
            changed_files = rp.get_changed_files(repo)
            docker_info = json.load(old_file)
            version_info = version_info + version_data_from_dict(docker_info, ['version','file'], [str(path) for path in changed_files], write=write)
            if write:
                json.dump(docker_info, new_file, indent=4)

        else:
            for i, line in enumerate(old_file):
                
                matches = re.finditer(regex_pattern, line)
                if not is_valid_version(file_path, line):
                    if write:
                        new_file.write(line)
                    continue

                for match in matches:
                    prev_ver_num = match.group()
                    new_version_num = update_version(prev_ver_num)
                    version_info.append((os.path.basename(file_path), new_version_num))
                    new_line = line.replace(prev_ver_num, new_version_num)
                    if write:
                        new_file.write(new_line)
                        print(f'Found on line {i+1}: {prev_ver_num}')
                        print(f'Changed {line.strip()} to {new_line.strip()}')
    if write:
        new_file.close()
        #Copy the file permissions from the old file to the new file
        shutil.copymode(file_path, abs_path)
        #Remove original file
        os.remove(file_path)
        #Move new file
        shutil.move(abs_path, file_path)

    return version_info



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
