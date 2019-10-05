#!/usr/bin/env python3
"""Garnet Linux agent.

Description:

    Uses Python2 to be compatible with most Linux systems

    This script:
        1) Retrieves a variety of system information
        2) Posts the data using HTTP to a server listed
           in the configuration file

"""
# Standard libraries
import sys
import socket
from time import sleep

# Garnet libraries
try:
    from garnet.agents import agent as Agent
except:
    print('You need to set your PYTHONPATH to include the Garnet library')
    sys.exit(2)
from garnet.utils import configuration
from garnet.utils import daemon
from garnet.agents import data_linux


class PollingAgent(object):
    """Garnet agent that gathers data.

    Args:
        None

    Returns:
        None

    Functions:
        __init__:
        populate:
        post:
    """

    def __init__(self):
        """Method initializing the class.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        self.agent_name = '_garnet'

        # Get configuration
        self.config = configuration.ConfigAgent(self.agent_name)

    def name(self):
        """Return agent name.

        Args:
            None

        Returns:
            value: Name of agent

        """
        # Return
        value = self.agent_name
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

            # Update the PID file timestamp (important)
            daemon.update_pid(self.name())

            # Sleep
            interval = self.config.interval()
            sleep(interval)

    def upload(self):
        """Post system data to the central server.

        Args:
            None

        Returns:
            None

        """
        # Get devicename
        devicename = socket.getfqdn()

        # Initialize key variables
        agent = Agent.Agent(self.config, devicename)

        # Update agent with linux data
        data_linux.getall(agent)

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
