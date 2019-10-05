#!/usr/bin/env python3
"""Pattoo helper for the Linux agent.

Description:

    Uses Python2 to be compatible with most Linux systems


"""
# Standard libraries
import os
import re
import platform
from collections import defaultdict

# pip3 libraries
import psutil


def getall(agent):
    """Get all agent data.

    Performance data on linux server on which this application is installed.

    Args:
        agent: Agent object

    Returns:
        None

    """
    # Update agent with system data
    _update_agent_system(agent)

    # Update agent with disk data
    _update_agent_disk(agent)

    # Update agent with network data
    _update_agent_net(agent)


def _update_agent_system(agent):
    """Update agent with system data.

    Args:
        agent: Agent object

    Returns:
        None

    """
    #########################################################################
    # Set non timeseries values
    #########################################################################

    agent.populate_single('release', platform.release(), base_type=None)
    agent.populate_single('system', platform.system(), base_type=None)
    agent.populate_single('version', platform.version(), base_type=None)
    dist = platform.linux_distribution()
    agent.populate_single('distribution', ' '.join(dist), base_type=None)
    agent.populate_single('cpu_count', psutil.cpu_count(), base_type=1)

    #########################################################################
    # Set timeseries values
    #########################################################################
    agent.populate_single(
        'process_count', len(psutil.pids()), base_type=1)

    agent.populate_named_tuple(
        psutil.cpu_times_percent(), prefix='cpu_times_percent', base_type=1)

    # Load averages
    (la_01, la_05, la_15) = os.getloadavg()
    agent.populate_single(
        'load_average_01min', la_01, base_type=1)
    agent.populate_single(
        'load_average_05min', la_05, base_type=1)
    agent.populate_single(
        'load_average_15min', la_15, base_type=1)

    # Get CPU times
    agent.populate_named_tuple(
        psutil.cpu_times(), prefix='cpu_times', base_type=64)

    # Get CPU stats
    agent.populate_named_tuple(
        psutil.cpu_stats(), prefix='cpu_stats', base_type=64)

    # Get memory utilization
    agent.populate_named_tuple(psutil.virtual_memory(), prefix='memory')


def _update_agent_disk(agent):
    """Update agent with disk data.

    Args:
        agent: Agent object

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
    agent.populate_dict(multikey, prefix='swap')
    agent.populate_dict(counterkey, prefix='swap', base_type=64)

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
    agent.populate_dict(multikey, prefix='disk_usage')

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
    agent.populate_dict(counterkey, prefix='disk_io', base_type=64)


def _update_agent_net(agent):
    """Update agent with network data.

    Args:
        agent: Agent object

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
    agent.populate_dict(counterkey, prefix='network', base_type=64)
