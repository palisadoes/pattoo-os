#!/usr/bin/env python3
"""Switchmap-NG ingest cache daemon.

Extracts agent data from cache directory files.

"""

# Standard libraries
from time import sleep
import sys
import os

# Try to create a working PYTHONPATH
_BIN_DIRECTORY = os.path.dirname(os.path.realpath(__file__))
_ROOT_DIRECTORY = os.path.abspath(os.path.join(_BIN_DIRECTORY, os.pardir))
if _BIN_DIRECTORY.endswith('/pattoo-os/bin') is True:
    sys.path.append(_ROOT_DIRECTORY)
else:
    print(
        'This script is not installed in the "pattoo-os/bin" directory. '
        'Please fix.')
    sys.exit(2)

# Pattoo libraries
from pattoo import post
from pattoo import configuration
from pattoo.pattoo import POLLER_EXECUTABLE
from pattoo import data
from pattoo import agent
from pattoo import log


class PollingAgent(agent.Agent):
    """Switchmap-NG agent that gathers data.

    Args:
        None

    Returns:
        None

    """

    def __init__(self, parent):
        """Initialize the class.

        Args:
            config_dir: Configuration directory

        Returns:
            None

        """
        # Initialize key variables
        agent.Agent.__init__(self, parent)

        # Initialize key variables
        self._agent_name = 'pattoo-os-actived'

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
        # Get system data
        data_dict = data.poll(self._config)

        # Post to remote server
        server = post.Data(data_dict)

        # Post data
        success = server.post()

        # Purge cache if success is True
        if success is True:
            server.purge()


def main():
    """Start the pattoo agent.

    Args:
        None

    Returns:
        None

    """
    # Get configuration
    agent_poller = PollingAgent(POLLER_EXECUTABLE)

    # Do control
    cli = agent.AgentCLI()
    cli.control(agent_poller)


if __name__ == "__main__":
    main()
