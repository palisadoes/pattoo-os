#!/usr/bin/env python3
"""Pattoo general library."""

import os
import sys
import time
import hashlib
import yaml

# Pattoo libraries
from pattoo import configuration
from pattoo import log
import pattoo


def root_directory():
    """Determine the root directory in which pattoo is installed.

    Args:
        None

    Returns:
        root_dir: Root directory

    """
    # Get the directory of the pattoo library
    pattoo_dir = pattoo.__path__[0]
    components = pattoo_dir.split(os.sep)

    # Determine the directory two levels above
    root_dir = os.sep.join(components[0:-1])

    # Return
    return root_dir


def encode(value):
    """Encode string value to utf-8.

    Args:
        value: String to encode

    Returns:
        result: encoded value

    """
    # Initialize key variables
    result = value

    # Start decode
    if value is not None:
        if isinstance(value, str) is True:
            result = value.encode()

    # Return
    return result


def decode(value):
    """Decode utf-8 value to string.

    Args:
        value: String to decode

    Returns:
        result: decoded value

    """
    # Initialize key variables
    result = value

    # Start decode
    if value is not None:
        if isinstance(value, bytes) is True:
            result = value.decode('utf-8')

    # Return
    return result


def hashstring(string, sha=256, utf8=False):
    """Create a UTF encoded SHA hash string.

    Args:
        string: String to hash
        length: Length of SHA hash
        utf8: Return utf8 encoded string if true

    Returns:
        result: Result of hash

    """
    # Initialize key variables
    listing = [1, 224, 384, 256, 512]

    # Select SHA type
    if sha in listing:
        index = listing.index(sha)
        if listing[index] == 1:
            hasher = hashlib.sha1()
        elif listing[index] == 224:
            hasher = hashlib.sha224()
        elif listing[index] == 384:
            hasher = hashlib.sha512()
        elif listing[index] == 512:
            hasher = hashlib.sha512()
        else:
            hasher = hashlib.sha256()

    # Encode the string
    hasher.update(bytes(string.encode()))
    device_hash = hasher.hexdigest()
    if utf8 is True:
        result = device_hash.encode()
    else:
        result = device_hash

    # Return
    return result


def validate_timestamp(timestamp):
    """Validate timestamp to be a multiple of 'interval' seconds.

    Args:
        timestamp: epoch timestamp in seconds

    Returns:
        valid: True if valid

    """
    # Initialize key variables
    valid = False
    interval = configuration.Config().interval()

    # Process data
    test = (int(timestamp) // interval) * interval
    if test == timestamp:
        valid = True

    # Return
    return valid


def normalized_timestamp(timestamp=None):
    """Normalize timestamp to a multiple of 'interval' seconds.

    Args:
        timestamp: epoch timestamp in seconds

    Returns:
        value: Normalized value

    """
    # Initialize key variables
    interval = configuration.Config().interval()

    # Process data
    if timestamp is None:
        value = (int(time.time()) // interval) * interval
    else:
        value = (int(timestamp) // interval) * interval
    # Return
    return value


def read_yaml_files(config_directory):
    """Read the contents of all yaml files in a directory.

    Args:
        config_directory: Directory with configuration files

    Returns:
        config_dict: Dict of yaml read

    """
    # Initialize key variables
    yaml_found = False
    yaml_from_file = ''
    all_yaml_read = ''

    if os.path.isdir(config_directory) is False:
        log_message = (
            'Configuration directory "{}" '
            'doesn\'t exist!'.format(config_directory))
        log.log2die(1009, log_message)

    # Cycle through list of files in directory
    for filename in os.listdir(config_directory):
        # Examine all the '.yaml' files in directory
        if filename.endswith('.yaml'):
            # YAML files found
            yaml_found = True

            # Read file and add to string
            file_path = '{}/{}'.format(config_directory, filename)
            try:
                with open(file_path, 'r') as file_handle:
                    yaml_from_file = file_handle.read()
            except:
                log_message = (
                    'Error reading file {}. Check permissions, '
                    'existence and file syntax.'
                    ''.format(file_path))
                log.log2die(1065, log_message)

            # Append yaml from file to all yaml previously read
            all_yaml_read = '{}\n{}'.format(all_yaml_read, yaml_from_file)

    # Verify YAML files found in directory. We cannot use logging as it
    # requires a logfile location from the configuration directory to work
    # properly
    if yaml_found is False:
        log_message = (
            'No configuration files found in directory "{}" with ".yaml" '
            'extension.'.format(config_directory))
        print(log_message)
        sys.exit(1)

    # Return
    config_dict = yaml.safe_load(all_yaml_read)
    return config_dict


def search_file(filename):
    """Run the cli_string UNIX CLI command and record output.

    Args:
        filename: File to find

    Returns:
        result: Result

    """
    # Initialize key variables
    result = None
    search_path = os.environ['PATH']

    paths = search_path.split(os.pathsep)
    for path in paths:
        if os.path.exists(os.path.join(path, filename)) is True:
            result = os.path.abspath(os.path.join(path, filename))
            break

    # Return
    return result


def all_same(items):
    """Determine if all items of a list are the same item.

    Args:
        items: List to verify

    Returns:
        result: Result

    """
    # Do test and return
    result = all(item == items[0] for item in items)
    return result
