#!/usr/bin/env python3
"""Pattoo language class.

Description:

    This class:
        1) Processes language for agents

"""
# Standard libraries
import os
import yaml

# Pattoo libraries
from utils import log
from utils import configuration
from utils import general


class Agent(object):
    """Class to handle languages for agents.

    Args:
        None

    Returns:
        None

    Functions:
        __init__:
        populate:
        post:
    """

    def __init__(self, agent_name):
        """Method initializing the class.

        Args:
            agent_name

        Returns:
            None

        """

        # Initialize key variables
        self.agent_name = agent_name
        self.agent_yaml = {}

        # Get the language used
        config = configuration.Config()
        lang = config.language()
        # Determine the agent's language yaml file
        root_directory = general.root_directory()
        yaml_file = (
            '%s/metadata/%s/agents/%s.yaml') % (
                root_directory, lang, self.agent_name)

        # Read the agent's language yaml file
        if os.path.exists(yaml_file) is True:
            with open(yaml_file, 'r') as file_handle:
                yaml_from_file = file_handle.read()
            self.agent_yaml = yaml.load(yaml_from_file)
        else:
            log_message = ('Agent language file %s does not exist.') % (
                yaml_file)
            log.log2warning(1034, log_message)

    def label_description(self, agent_label):
        """Return the name of the agent.

        Args:
            agent_label: Agent label

        Returns:
            value: Label description

        """
        # Initialize key variables
        value = ''
        data = {}
        top_key = 'agent_source_descriptions'

        if top_key in self.agent_yaml:
            data = self.agent_yaml[top_key]

        if agent_label in data:
            if 'description' in data[agent_label]:
                value = data[agent_label]['description']

        # Return
        return value

    def label_units(self, agent_label):
        """Return the name of the agent.

        Args:
            agent_label: Agent label

        Returns:
            value: Label units of measure

        """
        # Initialize key variables
        agent_label = agent_label.decode()
        value = ''
        data = {}
        top_key = 'agent_source_descriptions'

        if top_key in self.agent_yaml:
            data = self.agent_yaml[top_key]

        if agent_label in data:
            if 'units' in data[agent_label]:
                value = data[agent_label]['units']

        # Return
        return value
