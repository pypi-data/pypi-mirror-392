ipfabric_nornir
==============

## IP Fabric

[IP Fabric](https://ipfabric.io) is a vendor-neutral network assurance platform that automates the 
holistic discovery, verification, visualization, and documentation of 
large-scale enterprise networks, reducing the associated costs and required 
resources whilst improving security and efficiency.

It supports your engineering and operations teams, underpinning migration and 
transformation projects. IP Fabric will revolutionize how you approach network 
visibility and assurance, security assurance, automation, multi-cloud 
networking, and trouble resolution.

**Integrations or scripts should not be installed directly on the IP Fabric VM unless directly communicated from the
IP Fabric Support or Solution Architect teams.  Any action on the Command-Line Interface (CLI) using the root, osadmin,
or autoboss account may cause irreversible, detrimental changes to the product and can render the system unusable.**

# Special Thanks

This project is an IP Fabric officially supported fork of 
[nornir_ipfabric](https://github.com/routetonull/nornir_ipfabric) by [routetonull](https://github.com/routetonull/).  Thank you for your work!


# Install

The recommended way to install `ipfabric_nornir` is via pip

```sh
pip install ipfabric_nornir
```

# Requirements

An instance of [IP Fabric](https://ipfabric.io/) is required to collect information.


# Example usage

## Setup

### Using environment variables

Set environment vars to provide url and credentials to connect to the IP Fabric server

```sh
export IPF_URL=https://ipfabric.local
export IPF_TOKEN=myToken

# Or Username and Password
export IPF_USER=admin
export IPF_PASSWORD=mySecretPassword
```

### Using `.env` file

The easiest way to use this package is with a `.env` file.  You can copy the sample and edit it with your environment variables. 

```commandline
cp sample.env .env
```

This contains the following variables which can also be set as environment variables instead of a .env file.
```
IPF_URL="https://demo3.ipfabric.io"
IPF_TOKEN=TOKEN
IPF_VERIFY=true
```

Or if using Username/Password:
```
IPF_URL="https://demo3.ipfabric.io"
IPF_USERNAME=USER
IPF_PASSWORD=PASS
```

## Running

```python
from nornir import InitNornir
nr = InitNornir(inventory={"plugin": "IPFabricInventory"})
```


## Using the InitNornir function

Init

```python
from nornir import InitNornir
nr = InitNornir(
    inventory={
        "plugin": "IPFabricInventory",
        "options": {
            "base_url": "https://ipfabric.local",
            "token": "Token",  # or "username":"admin", "password":"mySecretPassword",
            "verify": True,
            "platform_map": "netmiko",  # "netmiko" (Default), "napalm", or "genie",
            "default": {"username": "device_username", "password": "device_password"},
        },
    },
)
```

## Using the Nornir configuration file

File *config.yaml*

```yaml
---
inventory:
  plugin: IPFInventory
  options:
    base_url: "https://ipfabric.local"
    token: "TOKEN"
    # username: "admin"
    # password: "mySecretPassword"
    verify: true
    platform_map: netmiko  # "netmiko", "napalm", or "genie"
    default:
      username: 'device_username'
      password: 'device_password'
```

Usage:

```python
from nornir import InitNornir
nr = InitNornir(config_file="config.yaml", inventory={"plugin": "IPFabricInventory"})
```
