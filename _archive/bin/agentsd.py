#!/usr/bin/env python3

"""Garnet ingest cache daemon.

Extracts agent data from cache directory files.

"""

# Standard libraries
import sys
import time


# Garnet libraries
try:
    from garnet.agents import agent as Agent
except:
    print('You need to set your PYTHONPATH to include the Garnet library')
    sys.exit(2)
from garnet.agents import check


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
            config_dir: Configuration directory

        Returns:
            None

        """
        # Initialize key variables
        self.agent_name = 'agentsd'

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
            check.process()
            time.sleep(15)


def main():
    """Process agent data.

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
