"""Module of pattoo webserver routes.

Contains all routes that pattoo's Flask webserver uses

"""
# Standard imports
from utils import log

# Pip imports
import requests


class Infoset(object):
    """Class that stores pattoo data that is repeatedly required.

    Args:
        None

    Returns:
        None

    """

    def __init__(self, config):
        """Method initializing the class.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        self.api = API(config)

        (self._idx_device, self._idx_agent) = self._pattoo_device_agent()

        if self._idx_device is None or self._idx_agent is None:
            log_message = ('Unable to contact API server.')
            log.log2die(1050, log_message)
        else:
            self._devicename = self._pattoo_devicename()

    def devicename(self):
        """Get pattoo devicename.

        Args:
            None

        Returns:
            value: Required value

        """
        # return
        value = self._devicename
        return value

    def idx_device(self):
        """Get pattoo idx_device.

        Args:
            None

        Returns:
            value: Required value

        """
        # return
        value = self._idx_device
        return value

    def idx_agent(self):
        """Get pattoo idx_agent.

        Args:
            None

        Returns:
            value: Required value

        """
        # return
        value = self._idx_agent
        return value

    def _pattoo_devicename(self):
        """Get devicename for _pattoo agent.

        Args:
            None

        Returns:
            device: Devicename

        """
        # Get device details and return
        uri = ('devices/%s') % (self.idx_device())
        device_data = self.api.get(uri)
        device = device_data['devicename']

        # Retun
        return device

    def _pattoo_device_agent(self):
        """Get DeviceAgent index information for _pattoo agent.

        Args:
            None

        Returns:
            device: Devicename

        """
        # Initialize key variables
        idx_agent = 1
        idx_device = 1
        device_agents_indices = self.api.get(
            'deviceagents')

        if device_agents_indices is not None:
            agents = self.api.get('agents')

            # Find pattoo in agents
            for agent in agents:
                if agent['agent'] == '_pattoo':
                    idx_agent = agent['idx_agent']

            # Find device index for idx_agent
            for device_agent in device_agents_indices:
                if device_agent['idx_agent'] == idx_agent:
                    idx_device = device_agent['idx_device']

            # Return
            return (idx_device, idx_agent)
        else:
            return (None, None)


class API(object):
    """Class gathers all configuration information.

    Args:
        None

    Returns:
        None

    Functions:
        __init__:
        devices:
        snmp_auth:
    """

    def __init__(self, config):
        """Function for intializing the class.

        Args:
            None

        Returns:
            None

        """
        # Initialize key variables
        self.config = config
        fixed_uri = config.api_server_uri().lstrip('/').rstrip('/')

        # Create API URL
        if config.api_server_https() is True:
            prefix = 'https'
        else:
            prefix = 'http'
        self.url_prefix = (
            '%s://%s:%s/%s'
            '') % (
                prefix, config.api_server_name(),
                config.api_server_port(), fixed_uri)

    def _url(self, uri):
        """Get api_data.

        Args:
            uri: URI to append to prefix

        Returns:
            result: Full URL to process

        """
        # Fix URI string
        fixed_uri = uri.lstrip('/').rstrip('/')

        # Create API URL
        result = ('%s/%s') % (self.url_prefix, fixed_uri)
        return result

    def get(self, uri):
        """Get api_data.

        Args:
            uri: URI to retrieve

        Returns:
            data: Result of query

        """
        # Initialize key variables
        data = None

        # Create API URL
        url = self._url(uri)
        # Return data
        try:
            result = requests.get(url)
            data = result.json()
        except Exception as e:
            print(e)
            data = None
        # Return
        return data

    def post(self, uri, data):
        """Get api_data.

        Args:
            uri: URI to retrieve

        Returns:
            _data: Result of query

        """
        # Initialize key variables
        success = False

        # Create API URL
        url = self._url(uri)
        try:
            result = requests.post(url, json=data)
            response = True
        except:
            response = False

        # Define success
        if response is True:
            if result.status_code == 200:
                success = True

        # Retun
        return success
