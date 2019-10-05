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
import time

# Garnet libraries
try:
    from agents import agent as Agent
except:
    print('You need to set your PYTHONPATH to include the Garnet library')
    sys.exit(2)
from etc import conf
from utils import configuration
from utils import daemon
from utils import log
from agents import data_linux


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
        self.agent_name = 'collectr'

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
            # daemon.update_pid(self.name())
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

        if conf.CUSTOM:
            conf.custom_collection(agent)
        else:
            # Update agent with linux data
            data_linux.getall(agent)

        # Post data
        print(time.time())
        success = agent.post()
        # Purge cache if success is True
        if success is True:
            log.log2console(2000, "Successfully posted data to infoset-db")
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
