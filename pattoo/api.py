#!/usr/bin/env python3
"""This is a test of flask."""

# Pip packages
from flask import Flask, jsonify

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
    return jsonify(data_dict)
