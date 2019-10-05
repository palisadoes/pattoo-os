#!/usr/bin/env python3
"""Pattoo classes that manage various configurations."""

import os.path
import os

# Import project libraries
from pattoo import general
from pattoo import log


class Config(object):
    """Class gathers all configuration information."""

    def __init__(self):
        """Initialize the class.

        Args:
            None

        Returns:
            None

        """
        # Update the configuration directory

        config_directory = '{}/etc'.format(general.root_directory())

        # Return data
        directories = [config_directory]
        self._config_dict = general.read_yaml_files(directories)

    def interval(self):
        """Get interval.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        key = 'main'
        sub_key = 'interval'
        intermediate = _key_sub_key(key, sub_key, self._config_dict, die=False)

        # Default to 300
        if intermediate is None:
            result = 300
        else:
            result = int(intermediate)
        return result

    def listen_address(self):
        """Get listen_address.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        key = 'passived'
        sub_key = 'listen_address'
        result = _key_sub_key(key, sub_key, self._config_dict, die=False)

        # Default to 0.0.0.0
        if result is None:
            result = '0.0.0.0'
        return result

    def bind_port(self):
        """Get bind_port.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        key = 'passived'
        sub_key = 'bind_port'
        intermediate = _key_sub_key(key, sub_key, self._config_dict, die=False)

        # Default to 6000
        if intermediate is None:
            result = 5000
        else:
            result = int(intermediate)
        return result

    def api_server_name(self):
        """Get api_server_name.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        key = 'actived'
        sub_key = 'api_server_name'

        # Get result
        result = _key_sub_key(key, sub_key, self._config_dict, die=False)
        if result is None:
            result = 'localhost'
        return result

    def api_server_port(self):
        """Get api_server_port.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        key = 'actived'
        sub_key = 'api_server_port'

        # Get result
        intermediate = _key_sub_key(key, sub_key, self._config_dict, die=False)
        if intermediate is None:
            result = 6000
        else:
            result = int(intermediate)
        return result

    def api_server_https(self):
        """Get api_server_https.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        key = 'actived'
        sub_key = 'api_server_https'

        # Get result
        result = _key_sub_key(key, sub_key, self._config_dict, die=False)
        if result is None:
            result = False
        return result

    def api_server_uri(self):
        """Get api_server_uri.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        key = 'actived'
        sub_key = 'api_server_uri'

        # Get result
        received = _key_sub_key(key, sub_key, self._config_dict, die=False)
        if received is None:
            received = 'pattoo/api/v1.0'

        # Trim leading slash if exists
        if received.startswith('/') is True:
            received = received[1:]
        if received.endswith('/') is True:
            received = received[:-1]

        # Return
        result = received
        return result

    def log_file(self):
        """Get log_file.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        sub_key = 'log_file'
        result = None
        key = 'main'

        # Get new result
        result = _key_sub_key(key, sub_key, self._config_dict)

        # Return
        return result

    def log_file_api(self):
        """Get log_file_api.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        _log_file = self.log_file()
        if _log_file.lower().endswith('.log') is True:
            result = '{}-api.log'.format(_log_file[0:-4])
        else:
            result = '{}-api.log'.format(_log_file)

        # Return
        return result

    def log_level(self):
        """Get log_level.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        sub_key = 'log_level'
        key = 'main'
        result = None

        # Return
        intermediate = _key_sub_key(key, sub_key, self._config_dict, die=False)
        if intermediate is None:
            result = 'debug'
        else:
            result = '{}'.format(intermediate).lower()
        return result

    def language(self):
        """Get language.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        sub_key = 'language'
        result = None
        key = 'main'

        # Get new result
        result = _key_sub_key(key, sub_key, self._config_dict)

        # Return
        return result

    def agent_cache_directory(self):
        """Determine the agent_cache_directory.

        Args:
            None

        Returns:
            value: configured agent_cache_directory

        """
        # Initialize key variables
        key = 'main'
        sub_key = 'agent_cache_directory'

        # Get result
        value = _key_sub_key(key, sub_key, self._config_dict)

        # Check if value exists
        if os.path.isdir(value) is False:
            log_message = (
                'agent_cache_directory: "{}" '
                'in configuration doesn\'t exist!'.format(value))
            log.log2die(1031, log_message)

        # Return
        return value

    def agent_subprocesses(self):
        """Get agent_subprocesses.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        key = 'main'
        sub_key = 'agent_subprocesses'
        result = _key_sub_key(key, sub_key, self._config_dict, die=False)

        # Default to 20
        if result is None:
            result = 20
        return result

    def agents(self):
        """Get agents.

        Args:
            None

        Returns:
            result: list of agents

        """
        # Initialize key variables
        key = 'agents'
        result = None

        # Verify data
        if key not in self._config_dict:
            log_message = ('No agents configured')
            log.log2die(1100, log_message)

        # Process agents
        result = self._config_dict[key]

        # Return
        return result

    def _config(self):
        """Get the config as a dict.

        Args:
            None

        Returns:
            data: configuration

        """
        # Initialize key variables
        data = self._config_dict
        return data


class ConfigAgent(Config):
    """Class gathers all configuration information."""

    def __init__(self, agent_name):
        """Initialize the class.

        Args:
            agent_name: Name of agent used to get descriptions
                from configuration subdirectory

        Returns:
            None

        """
        # Intialize key variables
        self._agent_name = agent_name

        # Instantiate the Config parent
        Config.__init__(self)

    def agent_name(self):
        """Get agent_name.

        Args:
            None

        Returns:
            result: result

        """
        # Get result
        result = self._agent_name
        return result


def _key_sub_key(key, sub_key, config_dict, die=True):
    """Get config parameter from YAML.

    Args:
        key: Primary key
        sub_key: Secondary key
        config_dict: Dictionary to explore
        die: Die if true and the result encountered is None

    Returns:
        result: result

    """
    # Get result
    result = None

    # Verify config_dict is indeed a dict.
    # Die safely as log_directory is not defined
    if isinstance(config_dict, dict) is False:
        log.log2die_safe(1021, 'Invalid configuration file. YAML not found')

    # Get new result
    if key in config_dict:
        # Make sure we don't have a None value
        if config_dict[key] is None:
            log_message = (
                '{}: value in configuration is blank. Please fix'.format(key))
            log.log2die_safe(1022, log_message)

        # Get value we need
        if sub_key in config_dict[key]:
            result = config_dict[key][sub_key]

    # Error if not configured
    if result is None and die is True:
        log_message = (
            '{}:{} not defined in configuration'.format(key, sub_key))
        log.log2die_safe(1016, log_message)

    # Return
    return result
