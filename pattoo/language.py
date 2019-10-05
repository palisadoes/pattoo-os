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
from pattoo import log
from pattoo import configuration
from pattoo import general


class Agent(object):
    """Manage agent languages."""

    def __init__(self, agent_name):
        """Initialize the class.

        Args:
            agent_name

        Returns:
            None

        """
        # Initialize key variables
        self._agent_name = agent_name
        self._agent_yaml = {}

        # Get the language used
        config = configuration.Config()
        lang = config.language()

        # Determine the agent's language yaml file
        root_directory = general.root_directory()
        yaml_file = (
            '{}/metadata/language/agents/{}/{}.yaml'.format(
                root_directory, lang, self._agent_name))

        # Read the agent's language yaml file
        if os.path.exists(yaml_file) is True:
            with open(yaml_file, 'r') as file_handle:
                yaml_from_file = file_handle.read()
            self._agent_yaml = yaml.safe_load(yaml_from_file)
        else:
            log_message = (
                'Agent language file {} does not exist for language type '
                '"{}" and agent {}. You may need to create one or request it '
                'as an "issue" on the pattoo GitHub site.'.format(
                yaml_file, lang, self._agent_name))
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

        if top_key in self._agent_yaml:
            data = self._agent_yaml[top_key]

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

        if top_key in self._agent_yaml:
            data = self._agent_yaml[top_key]

        if agent_label in data:
            if 'units' in data[agent_label]:
                value = data[agent_label]['units']

        # Return
        return value
