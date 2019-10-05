#!/usr/bin/env python3
"""Pattoo Linux agent.

Description:

    Uses Python2 to be compatible with most Linux systems

    This script:
        1) Retrieves a variety of system information
        2) Posts the data using HTTP to a server listed
           in the configuration file

"""
# Standard libraries
import sys
import os

# Create python path
EXEC_DIR = os.path.dirname(os.path.realpath(__file__))
PATH_DIR = os.path.abspath(os.path.join(EXEC_DIR, os.pardir))
if PATH_DIR.endswith('/pattoo-os') is True:
    sys.path.append(PATH_DIR)

# Pattoo libraries
try:
    from pattoo import pattoo
except:
    print('You need to set your PYTHONPATH to include the Pattoo library')
    sys.exit(2)
from pattoo import agent as Agent
from pattoo import configuration
from pattoo import log
from pattoo.api import API


class PollingAgent(object):
    """Pattoo agent that gathers data."""

    def __init__(self):
        """Initialize the class.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        self._agent_name = 'patoo-os-passived'

        # Get configuration
        self._config = configuration.Config()

    def name(self):
        """Return agent name.

        Args:
            None

        Returns:
            value: Name of agent

        """
        # Return
        value = self._agent_name
        return value

    def query(self):
        """Query all remote devices for data.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        if self._config.bind_port():
            data = self._config.bind_port()
            port = int(data)
        else:
            port = 5000

        # Do stuff
        log_message = (
            'Starting agent {} on TCP port {}.').format(self._agent_name, port)
        log.log2info(1088, log_message)
        API.run(host='0.0.0.0', port=port)


def main():
    """Start the agent.

    Args:
        None

    Returns:
        None

    """
    # Get configuration
    cli = Agent.AgentCLI()
    poller = PollingAgent()

    # Do control
    cli.control(poller)


if __name__ == "__main__":
    main()
