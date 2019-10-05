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
from time import sleep

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
from pattoo import data


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
        self._agent_name = 'patoo-os-actived'

        # Get configuration
        self._config = configuration.ConfigAgent(self._agent_name)

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
        # Post data to the remote server
        while True:
            self.upload()

            # Sleep
            interval = self._config.interval()
            sleep(interval)

    def upload(self):
        """Post system data to the central server.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        agent = Agent.Agent(self._config)

        # Update agent with linux data
        data.getall(agent)

        # Post data
        success = agent.post()

        # Purge cache if success is True
        if success is True:
            agent.purge()


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
