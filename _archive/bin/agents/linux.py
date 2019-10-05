#!/usr/bin/env python3
"""Garnet Sentry3 (Servertech intelligent CDU power strip) agent.

Description:

    This script:
        1) Retrieves a variety of system information
        2) Posts the data using HTTP to a server listed
           in the configuration file

"""
# Standard libraries
import sys
import json
from time import sleep

# Pip3 libraries
import requests

# Garnet libraries
try:
    from garnet.agents import agent as Agent
except:
    print('You need to set your PYTHONPATH to include the Garnet library')
    sys.exit(2)
from garnet.utils import configuration
from garnet.utils import daemon
from garnet.utils import log


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
        self.agent_name = 'linux'

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
            self._poll()

            # Sleep
            interval = self.config.interval()
            sleep(interval)

            # Update the PID file timestamp (important)
            daemon.update_pid(self.name())

    def _poll(self):
        """Query all remote devices for data.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        pollers = []

        # Create a list of polling objects
        devicenames = self.config.agent_devicenames()
        for devicename in devicenames:
            poller = Poller(devicename, self.agent_name)
            pollers.append(poller)

        # Start polling subprocesses
        if bool(pollers) is True:
            Agent.process(self.agent_name, pollers)


class Poller(object):
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

    def __init__(self, devicename, agent_name):
        """Method initializing the class.

        Args:
            devicename: Devicename to poll
            agent_name: Name of agent

        Returns:
            None

        """
        # Initialize key variables
        self.agent_name = agent_name
        self.devicename = devicename

        # Get configuration
        self.config = configuration.ConfigAgent(self.agent_name)

    def query(self):
        """Query all remote devices for data.

        Args:
            None

        Returns:
            None

        """
        # Define key variables
        get_success = False
        response = False

        # Create url
        if bool(self.config.agent_port()) is True:
            port = int(self.config.agent_port())
        else:
            port = 5001
        url = ('http://%s:%s') % (self.devicename, port)

        # Post data save to cache if this fails
        try:
            result = requests.get(url)
            response = True
        except:
            response = False

        # Define success
        if response is True:
            if result.status_code == 200:
                get_success = True

        if get_success is True:
            # Initialize key variables
            agent = Agent.Agent(self.config, self.devicename)

            # Post data after converting it to json from string
            data = json.loads(result.text)
            post_success = agent.post(data=data)

            # Purge cache if success is True
            if post_success is True:
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
