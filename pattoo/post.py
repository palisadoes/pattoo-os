#!/usr/bin/env python3
"""Pattoo Agent class.

Description:

    This script:
        1) Processes a variety of information from agents
        2) Posts the data using HTTP to a server listed
           in the configuration file

"""
# Standard libraries
import os
import socket
import json
from collections import defaultdict

# pip3 libraries
import requests

# Pattoo libraries
from pattoo import log
from pattoo import general
from pattoo import data as pattoo_data
from pattoo import configuration


class Data(object):
    """Pattoo agent that gathers data."""

    def __init__(self, _data):
        """Initialize the class.

        Args:
            _data: ConfigAgent configuration object
            agent_name: Name of agent

        Returns:
            None

        """
        # Initialize key variables
        self._data = _data

        # Get the agent_name
        if 'agent_program' in self._data:
            self._agent_name = self._data['agent_program']
        else:
            self._agent_name = ''

        # Get the agent ID
        config = configuration.ConfigAgent(self._agent_name)
        agent_id = pattoo_data.get_agent_id(config)

        # Construct URL for server
        if config.api_server_https() is True:
            prefix = 'https://'
        else:
            prefix = 'http://'
        self._url = (
            '{}{}:{}/{}/receive/{}'.format(
                prefix, config.api_server_name(),
                config.api_server_port(), config.api_server_uri(), agent_id))

        # Create the cache directory
        self._cache_dir = config.agent_cache_directory()
        if os.path.exists(self._cache_dir) is False:
            os.mkdir(self._cache_dir)

        # All cache files created by this agent will end with this suffix.
        devicehash = general.hashstring(self._data['devicename'], sha=1)
        self._cache_filename_suffix = '{}_{}.json'.format(agent_id, devicehash)

    def post(self, save=True, data=None):
        """Post data to central server.

        Args:
            save: When True, save data to cache directory if postinf fails
            data: Data to post. If None, then uses self._data (For testing)

        Returns:
            success: True: if successful

        """
        # Initialize key variables
        success = False
        response = False
        timestamp = self._data['timestamp']

        # Create data to post
        if data is None:
            data = self._data

        # Post data save to cache if this fails
        try:
            result = requests.post(self._url, json=data)
            response = True
        except:
            if save is True:
                # Create a unique very long filename to reduce risk of
                filename = '{}/{}_{}'.format(
                    self._cache_dir, timestamp, self._cache_filename_suffix)

                # Save data
                with open(filename, 'w') as f_handle:
                    json.dump(data, f_handle)

        # Define success
        if response is True:
            if result.status_code == 200:
                success = True

        # Log message
        if success is True:
            log_message = (
                'Agent "{}" successfully contacted server {}'
                ''.format(self._agent_name, self._url))
            log.log2info(1027, log_message)
        else:
            log_message = (
                'Agent "{}" failed to contact server {}'
                ''.format(self._agent_name, self._url))
            log.log2warning(1028, log_message)

        # Return
        return success

    def purge(self):
        """Purge data from cache by posting to central server.

        Args:
            None

        Returns:
            success: "True: if successful

        """
        # Initialize key variables
        agent_id = self._data['agent_id']

        # Add files in cache directory to list only if they match the
        # cache suffix
        all_filenames = [filename for filename in os.listdir(
            self._cache_dir) if os.path.isfile(
                os.path.join(self._cache_dir, filename))]
        filenames = [
            filename for filename in all_filenames if filename.endswith(
                self._cache_filename_suffix)]

        # Read cache file
        for filename in filenames:
            # Only post files for our own UID value
            if agent_id not in filename:
                continue

            # Get the full filepath for the cache file and post
            filepath = os.path.join(self._cache_dir, filename)
            with open(filepath, 'r') as f_handle:
                try:
                    data = json.load(f_handle)
                except:
                    # Log removal
                    log_message = (
                        'Error reading previously cached agent data file {} '
                        'for agent {}. May be corrupted.'
                        ''.format(filepath, self._agent_name))
                    log.log2die(1064, log_message)

            # Post file
            success = self.post(save=False, data=data)

            # Delete file if successful
            if success is True:
                os.remove(filepath)

                # Log removal
                log_message = (
                    'Purging cache file {} after successfully '
                    'contacting server {}'
                    ''.format(filepath, self._url))
                log.log2info(1029, log_message)
