#!/usr/bin/env python3
"""This is a test of flask."""

# Standard packages
import json
import logging

# Pip packages
from flask import Flask

# Pattoo imports
from pattoo import data
from pattoo.pattoo import API_PREFIX
from pattoo import configuration

# Define flask parameters
API = Flask(__name__)


@API.route(API_PREFIX)
def home():
    """Display api data on home page.

    Args:
        None

    Returns:
        None

    """
    # Initialize key variables
    agent_name = 'pattoo-os-passived'

    # Get configuration
    config = configuration.ConfigAgent(agent_name)

    # Return
    data_dict = data.poll(config)
    _data = json.dumps(data_dict)
    return _data


if __name__ == "__main__":
    API.logger.setLevel(logging.DEBUG)
    API.logger.addHandler()

    # Start app
    API.run(debug=True)
