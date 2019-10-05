#!/usr/bin/env python3
"""Switchmap WSGI script.

Serves as a Gunicorn WSGI entry point for pattoo-os

"""

# Standard libraries
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

# Switchmap libraries
from pattoo.agent import Agent, AgentAPI, AgentCLI
from pattoo.pattoo import API_EXECUTABLE, API_GUNICORN_AGENT


def main():
    """Main function to start the Gunicorn WSGI."""
    # Get PID filenename for Gunicorn
    agent_gunicorn = Agent(API_GUNICORN_AGENT)

    # Get configuration
    agent_api = AgentAPI(API_EXECUTABLE, API_GUNICORN_AGENT)

    # Do control (API first, Gunicorn second)
    cli = AgentCLI()
    cli.control(agent_api)
    cli.control(agent_gunicorn)


if __name__ == '__main__':
    main()
