#!/usr/bin/env python3
"""Pattoo Agent class.

Description:

    This script:
        1) Processes a variety of information from agents
        2) Posts the data using HTTP to a server listed
           in the configuration file

"""
# Standard libraries
import textwrap
import os
import sys
import json
import time
from collections import defaultdict
from multiprocessing import Pool
from random import random
import argparse
from copy import deepcopy

# pip3 libraries
import requests

# Pattoo libraries
from utils.daemon import Daemon
from utils import daemon
from utils import log
from utils import general
from utils import configuration
from metadata import language


class Agent(object):
    """Pattoo agent that gathers data.

    Args:
        None

    Returns:
        None

    Functions:
        __init__:
        populate:
        post:
    """

    def __init__(self, config, devicename):
        """Method initializing the class.

        Args:
            config: ConfigAgent configuration object
            agent_name: Name of agent
            devicename: Devicename that the agent applies to

        Returns:
            None

        """

        # Initialize key variables
        self.data = defaultdict(lambda: defaultdict(dict))
        agent_name = config.agent_name()
        id_agent = get_id_agent(config)
        self.lang = language.Agent(agent_name)

        # Add timestamp
        self.data['timestamp'] = general.normalized_timestamp()
        self.data['id_agent'] = id_agent
        self.data['agent'] = agent_name
        self.data['devicename'] = devicename

        # Construct URL for server
        if config.api_server_https() is True:
            prefix = 'https://'
        else:
            prefix = 'http://'
        self.url = (
            '%s%s:%s/%s/receive/%s') % (
                prefix, config.api_server_name(),
                config.api_server_port(), config.api_server_uri(), id_agent)

        # Create the cache directory
        self.cache_dir = config.agent_cache_directory()
        if os.path.exists(self.cache_dir) is False:
            os.mkdir(self.cache_dir)

        # All cache files created by this agent will end with this suffix.
        devicehash = general.hashstring(self.data['devicename'], sha=1)
        self.cache_suffix = ('%s_%s.json') % (id_agent, devicehash)

    def name(self):
        """Return the name of the agent.

        Args:
            None

        Returns:
            value: Name of agent

        """
        # Return
        value = self.data['agent']
        return value

    def populate(self, data_in):
        """Populate data for agent to eventually send to server.

        Args:
            data_in: dict of datapoint values from agent
            timeseries: TimeSeries data if True

        Returns:
            None

        """
        # Initialize data
        data = deepcopy(data_in)

        # Validate base_type
        if len(data) != 1 or isinstance(data, defaultdict) is False:
            log_message = ('Agent data "%s" is invalid') % (data)
            log.log2die(1025, log_message)

        # Get a description to use for label value
        for label in data.keys():
            description = self.lang.label_description(label)
            data[label]['description'] = description
            break

        # Add data to appropriate self.data key
        if data[label]['base_type'] is not None:
            self.data['timeseries'].update(data)
        else:
            self.data['timefixed'].update(data)

    def populate_single(self, label, value, base_type=None, source=None):
        """Populate a single value in the agent.

        Args:
            label: Agent label for data
            value: Value of data
            source: Source of the data
            base_type: Base type of data

        Returns:
            None

        """
        # Initialize key variables
        data = defaultdict(lambda: defaultdict(dict))
        data[label]['base_type'] = base_type
        data[label]['data'] = [[0, value, source]]

        # Update
        self.populate(data)

    def populate_named_tuple(self, named_tuple, prefix='', base_type=1):
        """Post system data to the central server.

        Args:
            named_tuple: Named tuple with data values
            prefix: Prefix to append to data keys when populating the agent
            base_type: SNMP style base_type (integer, counter32, etc.)

        Returns:
            None

        """
        # Get data
        system_dict = named_tuple._asdict()
        for label, value in system_dict.items():
            # Convert the dict to two dimensional dict keyed by [label][source]
            # for use by self.populate_dict
            new_label = ('%s_%s') % (prefix, label)

            # Initialize data
            data = defaultdict(lambda: defaultdict(dict))

            # Add data
            data[new_label]['data'] = [[0, value, None]]
            data[new_label]['base_type'] = base_type

            # Update
            self.populate(data)

    def populate_dict(self, data_in, prefix='', base_type=1):
        """Populate agent with data that's a dict keyed by [label][source].

        Args:
            data_in: Dict of data to post "X[label][source] = value"
            prefix: Prefix to append to data keys when populating the agent
            base_type: SNMP style base_type (integer, counter32, etc.)

        Returns:
            None

        """
        # Initialize data
        data_input = deepcopy(data_in)

        # Iterate over labels
        for label in data_input.keys():
            # Initialize tuple list to use by agent.populate
            value_sources = []
            new_label = ('%s_%s') % (prefix, label)

            # Initialize data
            data = defaultdict(lambda: defaultdict(dict))
            data[new_label]['base_type'] = base_type

            # Append to tuple list
            # (Sorting is important to keep consistent ordering)
            for source, value in sorted(data_input[label].items()):
                value_sources.append(
                    [source, value, source]
                )
            data[new_label]['data'] = value_sources

            # Update
            self.populate(data)

    def polled_data(self):
        """Return that that should be posted.

        Args:
            None

        Returns:
            None

        """
        # Return
        return self.data

    def post(self, save=True, data=None):
        """Post data to central server.

        Args:
            save: When True, save data to cache directory if postinf fails
            data: Data to post. If None, then uses self.data

        Returns:
            success: "True: if successful

        """
        # Initialize key variables
        success = False
        response = False
        timestamp = self.data['timestamp']
        id_agent = self.data['id_agent']

        # Create data to post
        if data is None:
            data = self.data

        # Post data save to cache if this fails
        try:
            result = requests.post(self.url, json=data)
            response = True
        except:
            if save is True:
                # Create a unique very long filename to reduce risk of
                filename = ('%s/%s_%s.json') % (
                    self.cache_dir, timestamp, self.cache_suffix)

                # Save data
                with open(filename, 'w') as f_handle:
                    json.dump(data, f_handle)

        # Define success
        if response is True:
            if result.status_code == 200:
                success = True

        # Log message
        if success is True:
            log_message = (
                'Agent "%s" successfully contacted server %s'
                '') % (self.name(), self.url)
            log.log2info(1027, log_message)
        else:
            log_message = (
                'Agent "%s" failed to contact server %s'
                '') % (self.name(), self.url)
            log.log2warning(1028, log_message)

        # Return
        return success

    def purge(self):
        """Purge data from cache by posting to central server.

        Args:
            None

        Returns:
            success: "True: if successful

        """
        # Initialize key variables
        id_agent = self.data['id_agent']

        # Add files in cache directory to list only if they match the
        # cache suffix
        all_filenames = [filename for filename in os.listdir(
            self.cache_dir) if os.path.isfile(
                os.path.join(self.cache_dir, filename))]
        filenames = [
            filename for filename in all_filenames if filename.endswith(
                self.cache_suffix)]

        # Read cache file
        for filename in filenames:
            # Only post files for our own UID value
            if id_agent not in filename:
                continue

            # Get the full filepath for the cache file and post
            filepath = os.path.join(self.cache_dir, filename)
            with open(filepath, 'r') as f_handle:
                try:
                    data = json.load(f_handle)
                except:
                    # Log removal
                    log_message = (
                        'Error reading previously cached agent data file %s '
                        'for agent %s. May be corrupted.'
                        '') % (filepath, self.name())
                    log.log2die(1064, log_message)

            # Post file
            success = self.post(save=False, data=data)

            # Delete file if successful
            if success is True:
                os.remove(filepath)

                # Log removal
                log_message = (
                    'Purging cache file %s after successfully '
                    'contacting server %s'
                    '') % (filepath, self.url)
                log.log2info(1029, log_message)


class AgentDaemon(Daemon):
    """Class that manages polling.

    Args:
        None

    Returns:
        None

    """

    def __init__(self, poller):
        """Method initializing the class.

        Args:
            poller: PollingAgent object

        Returns:
            None

        """
        # Instantiate poller
        self.poller = poller

        # Get PID filename
        agent_name = self.poller.name()
        pidfile = daemon.pid_file(agent_name)
        lockfile = daemon.lock_file(agent_name)

        # Call up the base daemon
        Daemon.__init__(self, pidfile, lockfile=lockfile)

    def run(self):
        """Start polling.

        Args:
            None

        Returns:
            None

        """
        # Start polling. (Poller decides frequency)
        while True:
            self.poller.query()


class AgentCLI(object):
    """Class that manages the agent CLI.

    Args:
        None

    Returns:
        None

    """

    def __init__(self):
        """Method initializing the class.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        self.parser = None

    def process(self, additional_help=None):
        """Return all the CLI options.

        Args:
            None

        Returns:
            args: Namespace() containing all of our CLI arguments as objects
                - filename: Path to the configuration file

        """
        # Header for the help menu of the application
        parser = argparse.ArgumentParser(
            description=additional_help,
            formatter_class=argparse.RawTextHelpFormatter)

        # CLI argument for starting
        parser.add_argument(
            '--start',
            required=False,
            default=False,
            action='store_true',
            help='Start the agent daemon.'
        )

        # CLI argument for stopping
        parser.add_argument(
            '--stop',
            required=False,
            default=False,
            action='store_true',
            help='Stop the agent daemon.'
        )

        # CLI argument for getting the status of the daemon
        parser.add_argument(
            '--status',
            required=False,
            default=False,
            action='store_true',
            help='Get daemon daemon status.'
        )

        # CLI argument for restarting
        parser.add_argument(
            '--restart',
            required=False,
            default=False,
            action='store_true',
            help='Restart the agent daemon.'
        )

        # CLI argument for stopping
        parser.add_argument(
            '--force',
            required=False,
            default=False,
            action='store_true',
            help=textwrap.fill(
                'Stops or restarts the agent daemon ungracefully when '
                'used with --stop or --restart.', width=80)
        )

        # Get the parser value
        self.parser = parser

    def control(self, poller):
        """Start the agent.

        Args:
            poller: PollingAgent object

        Returns:
            None

        """
        # Get the CLI arguments
        self.process()
        parser = self.parser
        args = parser.parse_args()

        # Run daemon
        _daemon = AgentDaemon(poller)
        if args.start is True:
            _daemon.start()
        elif args.stop is True:
            if args.force is True:
                _daemon.force()
            else:
                _daemon.stop()
        elif args.restart is True:
            if args.force is True:
                _daemon.force()
                _daemon.start()
            else:
                _daemon.restart()
        elif args.status is True:
            _daemon.status()
        else:
            parser.print_help()
            sys.exit(2)


def agent_sleep(agent_name, seconds=300):
    """Make agent sleep for a specified time, while updating PID every 300s.

    Args:
        agent_name: Name of agent
        seconds: number of seconds to sleep

    Returns:
        id_agent: UID for agent

    """
    # Initialize key variables
    interval = 300
    remaining = seconds

    # Start processing
    while True:
        # Update the PID file timestamp (important)
        daemon.update_pid(agent_name)

        # Sleep for at least "interval" number of seconds
        if remaining < interval:
            time.sleep(remaining)
            break
        else:
            time.sleep(interval)

        # Decrement remaining time
        remaining = remaining - interval


def get_id_agent(config):
    """Create a permanent UID for the agent.

    Args:
        config: ConfigAgent configuration object

    Returns:
        id_agent: UID for agent

    """
    # Initialize key variables
    agent_name = config.agent_name()
    filename = daemon.id_agent_file(agent_name)

    # Read environment file with UID if it exists
    if os.path.isfile(filename):
        with open(filename) as f_handle:
            id_agent = f_handle.readline()
    else:
        # Create a UID and save
        id_agent = _generate_id_agent()
        with open(filename, 'w+') as env:
            env.write(str(id_agent))

    # Return
    return id_agent


def _generate_id_agent():
    """Generate a UID.

    Args:
        None

    Returns:
        id_agent: the UID

    """
    # Create a UID and save
    prehash = ('%s%s%s%s%s') % (
        random(), random(), random(), random(), time.time())
    id_agent = general.hashstring(prehash)

    # Return
    return id_agent


def _process(poller):
    """Wrapper function to unpack arguments before calling the real function.

    Args:
        poller: Agent Poller object

    Returns:
        Nothing

    """
    # Execute query
    poller.query()


def process(agent_name, pollers):
    """Function where agents poll devices using multiprocessing.

    Args:
        agent_name: Agent name
        pollers: List of polling objects

    Returns:
        None

    """
    # Get configuration
    config = configuration.Config()
    configured_pool_size = config.agent_subprocesses()

    # Spawn processes only if we have files to process
    if bool(pollers) is True:
        # Process lock file
        lockfile = daemon.lock_file(agent_name)
        if os.path.exists(lockfile) is True:
            # Return if lock file is present
            log_message = (
                'Agent lock file %s exists. Multiple agent daemons '
                'running or the daemon may have died '
                'catastrophically in the past, in which case the lockfile '
                'should be deleted. Exiting agent process. '
                'Will try again later.'
                '') % (lockfile)
            log.log2warning(1044, log_message)
            return
        else:
            # Create lockfile
            open(lockfile, 'a').close()

        # Create a pool of sub process resources
        pool_size = int(min(configured_pool_size, len(pollers)))
        with Pool(processes=pool_size) as pool:
            # Create sub processes from the pool
            pool.map(_process, pollers)

        # Return if lock file is present
        if os.path.exists(lockfile) is True:
            os.remove(lockfile)
