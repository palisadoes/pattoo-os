#!/usr/bin/env python3
"""Pattoo helper for the Linux _data.

Description:

    Uses Python2 to be compatible with most Linux systems


"""
# Standard libraries
import os
import re
import platform
from collections import defaultdict
from copy import deepcopy
from random import random
import time
import socket
import distro

# pip3 libraries
import psutil

# Pattoo libraries
from pattoo import language
from pattoo import log
from pattoo import general
from pattoo import daemon


class _Data(object):
    """Pattoo agent that gathers data."""

    def __init__(self, config):
        """Initialize the class.

        Args:
            config: ConfigAgent configuration object

        Returns:
            None

        """
        # Initialize key variables
        self._data = defaultdict(lambda: defaultdict(dict))
        agent_name = config.agent_name()
        agent_id = get_agent_id(config)
        self._lang = language.Agent(agent_name)

        # Get devicename
        self._devicename = socket.getfqdn()

        # Add timestamp
        self._data['timestamp'] = general.normalized_timestamp()
        self._data['agent_id'] = agent_id
        self._data['agent_program'] = agent_name
        self._data['agent_hostname'] = self._devicename
        self._data['devices'] = defaultdict(
            lambda: defaultdict(lambda: defaultdict(lambda: defaultdict())))

    def name(self):
        """Return the name of the _data.

        Args:
            None

        Returns:
            value: Name of agent

        """
        # Return
        value = self._data['agent_program']
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
            log_message = 'Agent data "{}" is invalid'.format(data)
            log.log2die(1025, log_message)

        # Get a description to use for label value
        for label in data.keys():
            description = self._lang.label_description(label)
            data[label]['description'] = description
            break

        # Add data to appropriate self._data key
        if data[label]['base_type'] is not None:
            self._data['devices'][self._devicename]['timeseries'].update(data)
        else:
            self._data['devices'][self._devicename]['timefixed'].update(data)

    def populate_single(self, label, value, base_type=None, source=None):
        """Populate a single value in the _data.

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
        data[label]['data'] = [[source, value]]

        # Update
        self.populate(data)

    def populate_named_tuple(self, prefix, named_tuple, base_type=1):
        """Post system data to the central server.

        Args:
            prefix: Prefix to append to data keys when populating the agent
            named_tuple: Named tuple with data values
            base_type: SNMP style base_type (integer, counter32, etc.)

        Returns:
            None

        """
        # Get data
        system_dict = named_tuple._asdict()
        return_data = defaultdict(lambda: defaultdict(dict))
        data = []

        # Do nothing if there is no prefix
        if bool(prefix) is False:
            return

        # Cycle through results
        for label, value in system_dict.items():
            # Convert the dict to list of lists [label][value]
            data.append([label, value])

        # Add data
        return_data[prefix]['data'] = data
        return_data[prefix]['base_type'] = base_type

        # Update
        self.populate(return_data)

    def populate_dict(self, prefix, data_in, base_type=1):
        """Populate agent with data that's a dict keyed by [label][source].

        Args:
            prefix: Prefix to append to data keys when populating the agent
            data_in: Dict of data to post "X[label][source] = value"
            base_type: SNMP style base_type (integer, counter32, etc.)

        Returns:
            None

        """
        # Initialize data
        data_input = deepcopy(data_in)

        # Iterate over labels
        for label in data_input.keys():
            # Initialize tuple list to use by _data.populate
            value_sources = []
            new_label = '{}_{}'.format(prefix, label)

            # Initialize data
            data = defaultdict(lambda: defaultdict(dict))
            data[new_label]['base_type'] = base_type

            # Append to tuple list
            # (Sorting is important to keep consistent ordering)
            for source, value in sorted(data_input[label].items()):
                value_sources.append(
                    [source, value]
                )
            data[new_label]['data'] = value_sources

            # Update
            self.populate(data)

    def data(self):
        """Return that that should be posted.

        Args:
            None

        Returns:
            None

        """
        # Return
        return self._data


def poll(config):
    """Get all agent data.

    Performance data on linux server on which this application is installed.

    Args:
        config: ConfigAgent object

    Returns:
        None

    """
    # Intialize data gathering
    data = _Data(config)

    # Update agent with system data
    _get_data_system(data)

    # Update agent with disk data
    _get_data_storage(data)

    # Update agent with network data
    _get_data_network(data)

    #
    result = data.data()
    return result


def _get_data_system(_data):
    """Update agent with system data.

    Args:
        _data: Data object

    Returns:
        None

    """
    #########################################################################
    # Set non timeseries values
    #########################################################################

    _data.populate_single('release', platform.release(), base_type=None)
    _data.populate_single('system', platform.system(), base_type=None)
    _data.populate_single('version', platform.version(), base_type=None)
    dist = distro.linux_distribution()
    _data.populate_single('distribution', ' '.join(dist), base_type=None)
    _data.populate_single('cpu_count', psutil.cpu_count(), base_type=1)

    #########################################################################
    # Set timeseries values
    #########################################################################
    _data.populate_single(
        'process_count', len(psutil.pids()), base_type=1)

    _data.populate_named_tuple(
        'cpu_times_percent', psutil.cpu_times_percent(), base_type=1)

    # Load averages
    (la_01, la_05, la_15) = os.getloadavg()
    _data.populate_single(
        'load_average_01min', la_01, base_type=1)
    _data.populate_single(
        'load_average_05min', la_05, base_type=1)
    _data.populate_single(
        'load_average_15min', la_15, base_type=1)

    # Get CPU times
    _data.populate_named_tuple(
        'cpu_times', psutil.cpu_times(), base_type=64)

    # Get CPU stats
    _data.populate_named_tuple(
        'cpu_stats', psutil.cpu_stats(), base_type=64)

    # Get memory utilization
    _data.populate_named_tuple('memory', psutil.virtual_memory())


def _get_data_storage(_data):
    """Update agent with disk data.

    Args:
        _data: Data object

    Returns:
        None

    """
    # Initialize key variables
    regex = re.compile(r'^ram\d+$')

    # Get swap utilization
    multikey = defaultdict(lambda: defaultdict(dict))
    counterkey = defaultdict(lambda: defaultdict(dict))
    swap_data = psutil.swap_memory()
    system_list = swap_data._asdict()
    # "label" is named tuple describing partitions
    for label in system_list:
        value = system_list[label]
        if label in ['sin', 'sout']:
            counterkey[label][None] = value
        else:
            multikey[label][None] = value
    _data.populate_dict('swap', multikey)
    _data.populate_dict('swap', counterkey, base_type=64)

    # Get filesystem partition utilization
    disk_data = psutil.disk_partitions()
    multikey = defaultdict(lambda: defaultdict(dict))
    # "disk" is named tuple describing partitions
    for disk in disk_data:
        # "source" is the partition mount point
        source = disk.mountpoint
        if "docker" in str(source):
            pass
        else:
            system_data = psutil.disk_usage(source)
            system_dict = system_data._asdict()
            for label, value in system_dict.items():
                multikey[label][source] = value
    _data.populate_dict('disk_usage', multikey)

    # Get disk I/O usage
    io_data = psutil.disk_io_counters(perdisk=True)
    counterkey = defaultdict(lambda: defaultdict(dict))
    # "source" is disk name
    for source in io_data.keys():
        # No RAM pseudo disks. RAM disks OK.
        if bool(regex.match(source)) is True:
            continue
        system_data = io_data[source]
        system_dict = system_data._asdict()
        for label, value in system_dict.items():
            counterkey[label][source] = value
    _data.populate_dict('disk_io', counterkey, base_type=64)


def _get_data_network(_data):
    """Update agent with network data.

    Args:
        _data: Data object

    Returns:
        None

    """
    # Get network utilization
    nic_data = psutil.net_io_counters(pernic=True)
    counterkey = defaultdict(lambda: defaultdict(dict))
    for source in nic_data.keys():
        # "source" is nic name
        system_data = nic_data[source]
        system_dict = system_data._asdict()
        for label, value in system_dict.items():
            counterkey[label][source] = value
    _data.populate_dict('network', counterkey, base_type=64)


def get_agent_id(config):
    """Create a permanent UID for the _data.

    Args:
        config: ConfigAgent configuration object

    Returns:
        agent_id: UID for agent

    """
    # Initialize key variables
    agent_name = config.agent_name()
    filename = daemon.agent_id_file(agent_name)

    # Read environment file with UID if it exists
    if os.path.isfile(filename):
        with open(filename) as f_handle:
            agent_id = f_handle.readline()
    else:
        # Create a UID and save
        agent_id = _generate_agent_id()
        with open(filename, 'w+') as env:
            env.write(str(agent_id))

    # Return
    return agent_id


def _generate_agent_id():
    """Generate a UID.

    Args:
        None

    Returns:
        agent_id: the UID

    """
    # Create a UID and save
    prehash = '{}{}{}{}{}'.format(
        random(), random(), random(), random(), time.time())
    agent_id = general.hashstring(prehash)

    # Return
    return agent_id
