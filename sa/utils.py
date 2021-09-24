#!/usr/bin/env python

import json

def get_data_from_json(file):
    with open(file, 'r') as json_file:
        return json.load(json_file)


def find_key_pairs(obj, keys, found_pairs=[]):
    """Traverses a nested dictionary and lists to find a key, or list of key pairs and returns all parent dictionaries
        that contain the key/key pairs"""
    if not isinstance(keys, list):
        keys = [keys]

    if isinstance(obj, list):
        for obj in obj:
            find_key_pairs(obj, keys, found_pairs)
    elif isinstance(obj, dict):
        # check if all keys are in dictionary
        if not(keys - obj.keys()):
            # only update version number for files that have been modified
            found_pairs.append(obj)
        # check for a nested dictionary or list of dictionaries
        else:
            for k,v in obj.items():
                if isinstance(v, (dict, list)):
                    find_key_pairs(v, keys, found_pairs)

    return found_pairs
