#!/usr/bin/env python3
"""This is a test of flask."""

# Standard packages
import socket
import json
import logging

# Pip packages
from flask import Flask

from pattoo import agent as Agent
from pattoo import data as Data
from pattoo import configuration

# Define flask parameters
API = Flask(__name__)


@API.route('/')
def home():
    """Display api data on home page.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    agent_name = 'passived'

    # Get configuration
    config = configuration.ConfigAgent(agent_name)

    # Initialize key variables
    agent = Agent.Agent(config)

    # Update agent with linux data
    Data.getall(agent)

    # Return
    data_dict = agent.polled_data()
    _data = json.dumps(data_dict)
    return _data


if __name__ == "__main__":
    API.logger.setLevel(logging.DEBUG)
    API.logger.addHandler()

    # Start app
    API.run(debug=True)
