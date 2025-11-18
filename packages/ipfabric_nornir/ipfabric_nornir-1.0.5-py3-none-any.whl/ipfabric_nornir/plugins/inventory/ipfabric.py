"""ipfabric_nornir.inventory.ipfabric"""

import logging
from importlib import metadata
from nornir.core.inventory import Defaults, Groups, Host, Hosts, Inventory, ParentGroups, ConnectionOptions
from typing import Optional, Union, Literal

from ipfabric import IPFClient

logger = logging.getLogger(__name__)

"""
Map IPF family to netmiko platform names / netmiko device_type:
    IP Fabric supported device families https://docs.ipfabric.io/matrix/
    netmiko supported device_types https://github.com/ktbyers/netmiko/blob/master/netmiko/ssh_dispatcher.py
    napalm platform mapping https://napalm.readthedocs.io/en/latest/support/
    genie platform mapping https://github.com/CiscoTestAutomation/unicon.plugins/tree/master/src/unicon/plugins
"""
NETMIKO_MAP = {
    "asa": "cisco_asa",
    "ios": "cisco_ios",
    "ios-xe": "cisco_xe",
    "ios-xr": "cisco_xr",
    "nx-os": "cisco_nxos",
    "pa-os": "paloalto_panos",
    "wlc-air": "cisco_wlc",
    "junos": "juniper_junos",
    "aos": "alcatel_aos",
    "eos": "arista_eos",
    "fastiron": "brocade_fastiron",
    "gaia": "checkpoint_gaia",
    "gaia-embedded": "checkpoint_gaia",
    "ftd": "cisco_ftd",
    "viptela": "cisco_viptela",
    "os10": "dell_os10",
    "powerconnect": "dell_powerconnect",
    "ftos": "dell_force10",
    "exos": "extreme_exos",
    "prisma": "cloudgenix_ion",
    "fortigate": "fortinet",
    "comware": "hp_comware",
    "vrp": "huawei_vrp",
    "routeros": "mikrotik_routeros",
    "enterasys": "enterasys",
    # "timos"
    # aruba
    # "big-ip: "f5_ltm",
    # extreme boss, voss
}

NAPALM_MAP = {
    "nx-os": "nxos_ssh",
    "ios": "ios",
    "ios-xe": "ios",
    "ios-rx": "iosxr",
    "eos": "eos",
    "junos": "junos",
}

GENIE_MAP = {
    "nx-os": "nxos",
    "ios": "ios",
    "ios-xe": "iosxe",
    "ios-rx": "iosxr",
    "asa": "asa",
    "apic": "apic",
    "comware": "comware",
    "viptela": "viptela",
    "junos": "junos",
    "eos": "eos",
}

PLATFORM_MAP = {
    "netmiko": NETMIKO_MAP,
    "napalm": NAPALM_MAP,
    "genie": GENIE_MAP,
}


class IPFabricInventory(Inventory):
    """
    class IPFabricInventory(Inventory):
    """

    def __init__(
        self,
        base_url: Optional[str] = None,
        token: Optional[str] = None,
        snapshot_id: Optional[str] = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        verify: Union[bool, str] = True,
        platform_map: Literal["netmiko", "napalm", "genie"] = "netmiko",
        default: Optional[dict] = None,
        connection_options: Optional[dict] = None,
        **ipfabric_kwargs,
    ):
        """
        IP Fabric SDK Docs: https://gitlab.com/ip-fabric/integrations/python-ipfabric
        """
        self.ipf = IPFClient(
            base_url=base_url,
            auth=(username, password) if username and password else token,
            snapshot_id=snapshot_id,
            verify=verify,
            **ipfabric_kwargs,
        )
        self.ipf._client.headers["User-Agent"] = f'ipfabric_nornir/{metadata.version("ipfabric_nornir")}'
        self.platform_map = PLATFORM_MAP[platform_map]
        self.default = default or {}
        self.connection_options = (
            {k: ConnectionOptions(**v) for k, v in connection_options.items()} if connection_options else {}
        )

    def load(self) -> Inventory:
        """
        Load inventory
        """
        hosts = Hosts()
        groups = Groups()

        defaults = Defaults(username=self.default.get("username", None), password=self.default.get("password", None))

        for device in self.ipf.devices.all:
            data = {
                "address": (str(device.login_ip.ip) if device.login_ip else device.hostname,),
                "family": device.family or device.vendor,
                "hostname": device.hostname,
                "ipf_platform": device.platform,
                "protocol": device.login_type,
                "serial": device.sn_hw,
                "ipf_serial": device.sn,
                "sn_hw": device.sn_hw,
                "sn": device.sn,
                "site": device.site_name,
                "site_name": device.site_name,
                "vendor": device.vendor,
                "version": device.version,
                "fqdn": device.fqdn,
                "image": device.image,
                "model": device.model,
                "dev_type": device.dev_type,
            }

            hosts[device.sn] = Host(
                name=device.hostname,
                hostname=str(device.login_ip.ip) if device.login_ip else device.hostname,
                port=22 if device.login_type == "ssh" else 23,
                platform=self.platform_map.get(device.family, device.platform or device.vendor),
                username=defaults.username if defaults.username else None,
                password=defaults.password if defaults.password else None,
                groups=ParentGroups(),
                data=data,
                connection_options=self.connection_options,
                defaults=defaults,
            )

        return Inventory(hosts=hosts, groups=groups, defaults=defaults)
