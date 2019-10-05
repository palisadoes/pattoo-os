#!/usr/bin/env python3
"""Pattoo classes that manage various configurations."""

import os.path
import os

# Import project libraries
from utils import general
from utils import log


class Config(object):
    """Class gathers all configuration information.

    Args:
        None

    Returns:
        None

    Functions:
        __init__:
        devices:
        snmp_auth:
    """

    def __init__(self):
        """Function for intializing the class.

        Args:
            None

        Returns:
            None

        """
        # Update the configuration directory

        config_directory = ('%s/etc') % (general.root_directory())

        # Return data
        directories = [config_directory]
        self.config_dict = general.read_yaml_files(directories)

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
        intermediate = _key_sub_key(key, sub_key, self.config_dict, die=False)

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
        key = 'main'
        sub_key = 'listen_address'
        result = _key_sub_key(key, sub_key, self.config_dict, die=False)

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
        key = 'main'
        sub_key = 'bind_port'
        intermediate = _key_sub_key(key, sub_key, self.config_dict, die=False)

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
        key = 'main'
        sub_key = 'api_server_name'

        # Get result
        result = _key_sub_key(key, sub_key, self.config_dict, die=False)
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
        key = 'main'
        sub_key = 'api_server_port'

        # Get result
        intermediate = _key_sub_key(key, sub_key, self.config_dict, die=False)
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
        key = 'main'
        sub_key = 'api_server_https'

        # Get result
        result = _key_sub_key(key, sub_key, self.config_dict, die=False)
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
        key = 'main'
        sub_key = 'api_server_uri'

        # Get result
        received = _key_sub_key(key, sub_key, self.config_dict, die=False)
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
        result = _key_sub_key(key, sub_key, self.config_dict)

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
        intermediate = _key_sub_key(key, sub_key, self.config_dict, die=False)
        if intermediate is None:
            result = 'debug'
        else:
            result = (('%s') % (intermediate)).lower()
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
        result = _key_sub_key(key, sub_key, self.config_dict)

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
        value = _key_sub_key(key, sub_key, self.config_dict)

        # Check if value exists
        if os.path.isdir(value) is False:
            log_message = (
                'agent_cache_directory: "%s" '
                'in configuration doesn\'t exist!') % (value)
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
        result = _key_sub_key(key, sub_key, self.config_dict, die=False)

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
        if key not in self.config_dict:
            log_message = ('No agents configured')
            log.log2die(1100, log_message)

        # Process agents
        result = self.config_dict[key]

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
        data = self.config_dict
        return data


class ConfigAgent(Config):
    """Class gathers all configuration information.

    Args:
        None

    Returns:
        None

    Functions:
        __init__:
        devices:
        snmp_auth:
    """

    def __init__(self, agent_name):
        """Function for intializing the class.

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

        # Get config as dictionary
        self.config_dict = self._config()

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

    def agent_enabled(self):
        """Get agent_enabled.

        Args:
            None

        Returns:
            result: result

        """
        # Get config
        agent_config = _agent_config(self.agent_name(), self.config_dict)

        # Get result
        if 'agent_enabled' in agent_config:
            result = bool(agent_config['agent_enabled'])
        else:
            result = False
        return result

    def monitor_agent_pid(self):
        """Get monitor_agent_pid.

        Args:
            None

        Returns:
            result: result

        """
        # Get config
        agent_config = _agent_config(self.agent_name(), self.config_dict)

        # Get result
        if 'monitor_agent_pid' in agent_config:
            result = bool(agent_config['monitor_agent_pid'])
        else:
            result = False
        return result

    def agent_filename(self):
        """Get agent_filename.

        Args:
            None

        Returns:
            result: result

        """
        # Get config
        agent_config = _agent_config(self.agent_name(), self.config_dict)

        # Get result
        result = agent_config['agent_filename']
        return result

    def agent_devicenames(self):
        """Get agent_devicenames.

        Args:
            None

        Returns:
            result: result

        """
        # Initialize key variables
        result = []

        # Get config
        agent_config = _agent_config(self.agent_name(), self.config_dict)

        # Get result
        if 'agent_devicenames' in agent_config:
            if isinstance(agent_config['agent_devicenames'], list) is True:
                result = sorted(agent_config['agent_devicenames'])

        # Return
        return result

    def agent_port(self):
        """Get agent_port.

        Args:
            None

        Returns:
            result: result

        """
        # Get config
        agent_config = _agent_config(self.agent_name(), self.config_dict)

        # Get result
        if 'agent_port' in agent_config:
            result = agent_config['agent_port']
        else:
            result = []

        # Return
        return result

    def agent_metadata(self):
        """Get agent_metadata.

        Args:
            None

        Returns:
            result: result

        """
        # Get config
        agent_config = _agent_config(self.agent_name(), self.config_dict)

        # Get result
        if 'agent_metadata' in agent_config:
            result = agent_config['agent_metadata']
        else:
            result = []

        # Return
        return result


def _agent_config(agent_name, config_dict):
    """Get agent config parameter from YAML.

    Args:
        agent_name: Agent Name
        config_dict: Dictionary to explore
        die: Die if true and the result encountered is None

    Returns:
        result: result

    """
    # Get result
    key = 'agents'
    result = None

    # Get new result
    if key in config_dict:
        configurations = config_dict[key]
        for configuration in configurations:
            if 'agent_name' in configuration:
                if configuration['agent_name'] == agent_name:
                    result = configuration
                    break

    # Error if not configured
    if result is None:
        log_message = (
            'Agent %s not defined in configuration in '
            'agents:%s section') % (key, key)
        log.log2die(1094, log_message)

    # Return
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
            log_message = ('%s: value in configuration is blank. Please fix')
            log.log2die_safe(1022, log_message)

        # Get value we need
        if sub_key in config_dict[key]:
            result = config_dict[key][sub_key]

    # Error if not configured
    if result is None and die is True:
        log_message = (
            '%s:%s not defined in configuration') % (key, sub_key)
        log.log2die_safe(1016, log_message)

    # Return
    return result
