# pattoo-os

`pattoo-os` provide performance data on any Linux system it runs on. The data is presented in `json` format and can either be posted using HTTP to a remote server or viewed on the server on which it runs by visiting a well known URL.

The `json` data is formatted for easy ingestion by [pattooDB](https://github.com/PalisadoesFoundation/pattoo-ng)

## Installation
The steps are simple.

* Install the required packages
```
$ sudo pip3 install -r pip_requirements.txt
```
* Populate the configuration file.
* Start the desired daemons.
* Add the daemons to `systemd` so they start on reboot.

## Usage

`pattoo-os` contains two daemons.

1. `pattoo-os-actived.py` which will post `linux` system data in `json` format to a remote server
1. `pattoo-os-passived.py` which will make the same `linux` system data in `json` format available for viewing on the local server.

Both daemons will read any `.yaml` file found in the `etc/`directory for configuration parameters. Most persons will just use a single file called `config.yaml`

###
```bash
$ bin/pattoo-os-actived.py --help
usage: pattoo-os-actived.py [-h] [--start] [--stop] [--status] [--restart]
                            [--force]

optional arguments:
  -h, --help  show this help message and exit
  --start     Start the agent daemon.
  --stop      Stop the agent daemon.
  --status    Get daemon daemon status.
  --restart   Restart the agent daemon.
  --force     Stops or restarts the agent daemon ungracefully when used with --stop or
              --restart.
$
```


```bash
$ bin/pattoo-os-passived.py --help
usage: pattoo-os-passived.py [-h] [--start] [--stop] [--status] [--restart]
                             [--force]

optional arguments:
  -h, --help  show this help message and exit
  --start     Start the agent daemon.
  --stop      Stop the agent daemon.
  --status    Get daemon daemon status.
  --restart   Restart the agent daemon.
  --force     Stops or restarts the agent daemon ungracefully when used with --stop or
              --restart.
$
```


## Configuration

Edit `etc/config.yaml` to change configuration options

```yaml
main:
    log_level: debug
    log_directory: ~/GitHub/pattoo-os/log
    agent_cache_directory: ~/GitHub/pattoo-os/cache
    language: en
    interval: 300

pattoo-os-passived:
    listen_address: 0.0.0.0
    bind_port: 5000

pattoo-os-actived:
    api_server_name: 192.168.1.100
    api_server_port: 6000
    api_server_https: False
    api_server_uri: /pattoo/post

```
### Configuration Explanation

This table outlines how the 

|Section | Config Options          | Description                    |
|--|--|--|
| `main` |||
||  `log_directory` | Path to logging directory. Make sure the username running the daemons have RW access to files there. |
||  `log_level` | Default level of logging. `debug` is best for troubleshooting. |
|| `agent_cache_directory` | Directory of unsuccessful data posts to `pattoodb`|
|| `language` | Language  to be used in reporting statistics in JSON output. Language files can be found in the `metadata/language/agents/` directory.|
|| `interval`              | Interval of data collection and posting in seconds   |
| `pattoo-os-passived` | | |
|| `listen_address` | IP address on which the API server will listen. Setting this to `0.0.0.0` will make it listen on all IPv4 addresses. Setting to `"0::"` will make it listen on all IPv6 configured interfaces. It will not listen on IPv4 and IPv6 addresses simultaneously. You must **quote** all IPv6 addresses.|
|| `bind_port`              | TCP port on which the API will listen|
| `pattoo-os-actived` |||
|| `api_server_name`       | IP address of remote `pattoodb` server      |
|| `api_server_port`       | Port of remote `pattoodb` server     |
|| `api_server_https`      | Use `https` when sending data  to remote `pattoodb` server|
|| `api_server_uri`        | Remote `pattoodb` route prefix       |

## JSON Data Format

The `json` data formatting can be found in the [DATA.md](DATA.md) file

## Testing
If you are running `pattoo-os` on your local system, then you can test it by pointing your browser to `http://localhost:5000/pattoo` to view the system data.

## Troubleshooting
Check the log files in the `log_directory` specified in your configuration.