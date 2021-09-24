#!/usr/bin/env python

import os, re, pathlib, json, copy, _thread
import docker
from sa import utils


def build(build_files):
    """Build and tag docker containers based on information provided in 'docker-info.json' files"""
    images_info=[]
    client = docker.from_env()

    for build_file in build_files:
        docker_file_data = utils.get_data_from_json(build_file)
        docker_build_info = utils.find_key_pairs(docker_file_data, ['img_name','file','tags','version','docker_registries'])
        
        for build_info in docker_build_info:
            temp_dict = {}

            temp_dict['path'] = str(pathlib.Path(build_info['file']).parent.resolve())
            temp_dict['dockerfile'] = str(pathlib.Path(build_info['file']).resolve())
            temp_dict['pull'] = True
            # TODO: add a way to process CLI options with variables, or from ENV variables
            temp_dict['buildargs'] = build_info['build_args']
            
            # add versions to tags
            for i in range(len(build_info['tags'])):
                build_info['tags'][i] = ''.join([build_info['tags'][i],'-',build_info['version']])

            # add default tag and registry if not preset
            build_info['docker_registries'].append('')
            build_info['tags'].append(build_info['version'])
            build_info['tags'].append('latest')

            # dedup lists
            build_info['docker_registries'] = list(set(build_info['docker_registries']))
            build_info['tags'] = list(set(build_info['tags']))

            # add image name to tag
            for i in range(len(build_info['tags'])):
                build_info['tags'][i] = ''.join([build_info['img_name'],':',build_info['tags'][i]])

            # implement tags and remotes
            for registry in build_info['docker_registries']:
                for tag in build_info['tags']:
                    temp_dict['tag'] = tag
                    if registry != '':
                        temp_dict['tag'] = ''.join([registry,'/',tag])
                    images_info.append(copy.deepcopy(temp_dict))

    for image_info in images_info:
        # Build and tag all images
        results = client.images.build(**image_info)
        for logs in results[-1]:
            for k,v in logs.items():
                if isinstance(v, str):
                    print(v.strip())
                    continue
                print(v)
                
        #_thread.start_new_thread(client.images.build,**image_info)


def push():
    pass
