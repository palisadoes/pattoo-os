#!/usr/bin/env python3

"""Demonstration Script that extracts agent data from cache directory files.

This could be a modified to be a daemon

"""

# Standard libraries
import os
import time
import subprocess

# Pip3 libraries
import psutil

# Pattoo libraries
from utils import configuration
from utils import log
from utils import daemon
from utils import general


def process():
    """Make sure the correct agents are running.

    Args:
        None

    Returns:
        None

    """
    # Get list of configured agents
    config = configuration.Config()
    agents = config.agents()

    # Process each agent
    for agent_dict in agents:
        # Get agent_name
        agent_name = agent_dict['agent_name']
        agentconfig = configuration.ConfigAgent(agent_name)

        # Check for agent existence
        if agentconfig.agent_enabled() is True:
            _check_when_enabled(agentconfig)

        else:
            # Shutdown agent if running
            _check_when_disabled(agentconfig)


def _check_when_disabled(config):
    """Stop agent.

    Args:
        agent_filepath: Filepath of agent to be restarted.
        agent_name: Agent name

    Returns:
        None

    """
    # Get agent status variables
    agent_name = config.agent_name()
    pidfile = daemon.pid_file(agent_name)

    # Shutdown agent if running
    if os.path.isfile(pidfile) is True:
        with open(pidfile, 'r') as f_handle:
            pidvalue = int(f_handle.readline().strip())
        if psutil.pid_exists(pidvalue) is True:
            log_message = (
                'Agent "%s" is alive, but should be disabled. '
                'Attempting to stop.'
                '') % (agent_name)
            log.log2info(1032, log_message)
            _stop(config)


def _check_when_enabled(config):
    """Stop agent.

    Args:
        config: Agent configuration object

    Returns:
        None

    """
    # Initialize key variables
    agent_name = config.agent_name()
    agent_filepath = _agent_filepath(config)

    # Get agent status variables
    pidfile = daemon.pid_file(agent_name)
    lockfile = daemon.lock_file(agent_name)

    # Ignore agents that cannot be found
    if os.path.isfile(agent_filepath) is False:
        log_message = (
            'Agent executable file %s listed in the '
            'configuration file '
            'of agent "%s" does not exist. Please fix.'
            '') % (agent_filepath, agent_name)
        log.log2info(1075, log_message)
        return

    # Check for pid file
    if os.path.isfile(pidfile) is True:
        with open(pidfile, 'r') as f_handle:
            pidvalue = int(f_handle.readline().strip())

        # Check if service died catastrophically. No PID file
        if psutil.pid_exists(pidvalue) is False:
            log_message = (
                'Agent "%s" is dead. Attempting to restart.'
                '') % (agent_name)
            log.log2info(1041, log_message)

            # Remove PID file and restart
            os.remove(pidfile)
            _restart(config)

        else:
            # Check if agent hung without updating the PID
            if config.monitor_agent_pid() is True:
                try:
                    mtime = os.path.getmtime(pidfile)
                except OSError:
                    mtime = 0
                if mtime < int(time.time()) - (60 * 10):
                    log_message = (
                        'Agent "%s" is hung. Attempting to restart.'
                        '') % (agent_name)
                    log.log2info(1076, log_message)
                    _restart(config)
    else:
        if os.path.isfile(lockfile) is True:
            _restart(config)
        else:
            _start(config)


def _stop(config):
    """Stop agent.

    Args:
        config: Agent configuration object

    Returns:
        None

    """
    # Initialize key variables
    agent_name = config.agent_name()
    agent_filepath = _agent_filepath(config)

    # Restart
    log_message = (
        'Stopping agent "%s".'
        '') % (agent_name)
    log.log2info(1033, log_message)
    command2run = ('%s --stop --force') % (agent_filepath)
    _execute(command2run)


def _start(config):
    """Start agent.

    Args:
        config: Agent configuration object

    Returns:
        None

    """
    # Initialize key variables
    agent_name = config.agent_name()
    agent_filepath = _agent_filepath(config)

    # Start
    log_message = (
        'Starting agent "%s".'
        '') % (agent_name)
    log.log2info(1077, log_message)
    command2run = ('%s --start') % (agent_filepath)
    _execute(command2run)


def _restart(config):
    """Restart agent.

    Args:
        agent_filepath: Filepath of agent to be restarted.
        agent_name: Agent name

    Returns:
        None

    """
    # Restart
    _stop(config)
    _start(config)


def _agent_filepath(config):
    """Return the path to the agent.

    Args:
        config: Agent configuration object

    Returns:
        agent_filepath: Complete file path

    """
    # Initialize key variables
    agent_filename = config.agent_filename()

    # Get agent status variables
    root_dir = general.root_directory()
    agent_filepath = ('%s/%s') % (root_dir, agent_filename)

    # Return
    return agent_filepath


def _execute(command):
    """Run command on CLI.

    Args:
        command: Command to run

    Returns:
        None

    """
    # Run command
    subprocess.run(command.split())


if __name__ == "__main__":
    # Run the process function if we execute this file from the CLI
    process()
