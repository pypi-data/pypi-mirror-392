from typing import Dict, List, Literal
import urllib3
from napalm.base import models as napalm_models, NetworkDriver

import math
import re
import ipaddress
import netaddr

from pyaoscx.session import Session
from pprint import pprint
from ..base import SCBaseNetconfDriver
from .. import models

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

DEFAULT_VERSION = "10.04"


class SCAOSCXDriver(NetworkDriver, SCBaseNetconfDriver):
    """
    Current scaos napalm driver is old and only supports api v1, which is
    deprecated. So we are writing our own one. Woot!
    """

    netmiko_host_type = "aruba_aoscx"

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """NAPALM Constructor for AOS-CX."""
        if optional_args is None:
            optional_args = {}

        if "version" not in optional_args:
            optional_args["version"] = DEFAULT_VERSION
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout
        self.platform = "aoscx"

        # Hack to get IPv6 rest calls to work - need the IP address to be encased
        # in brackets
        try:
            ipaddress.IPv6Address(hostname)
            hostname = f"[{hostname}]"
        except ValueError:
            pass

        self.session = Session(hostname, optional_args["version"])

    def open(self):
        """
        Implementation of NAPALM method 'open' to open a connection to the device.
        """
        self.session.open(self.username, self.password)

    def close(self):
        """
        Implementation of NAPALM method 'close'. Closes the connection to the device and does
        the necessary cleanup.
        """
        self.session.close()

    def _get(self, path: str, attrs: list = None, depth: int = 1):
        path = re.sub(r"/rest/v.+?/", "", path)
        params = None
        if attrs:
            params = {"attributes": ",".join(attrs), "depth": depth}
        r = self.session.request("GET", path, params=params)
        r.raise_for_status()
        return r.json()

    def _iter_get(
        self, path: str, sub_path: str = None, attrs=None, depth=1
    ) -> dict[str, any]:
        """
        Iterate through a dict of paths at 'path', doing rest 'gets' for the
        a particular sub_path on each one with the specificed attributes and depth
        :path: base path, eg 'system/interfaces'
        :sub_path: append to the base path, eg 'lldp_neighbors'
        :attrs: restrict output at each sub_path

        returns dict of data mapping to each key in the original path
        """
        results = {}
        paths = self._get(path, depth=1)
        for k, v in paths.items():
            full_path = f"{v}/{sub_path}" if sub_path else v
            results[k] = self._get(full_path, attrs, depth=depth)

        return results

    def json_lookup(self, data, key_name, default_value="", one_match=True):
        result = []
        self._json_lookup(data, key_name, result, one_match=one_match)

        if not result:
            return default_value
        if one_match:
            return result[0]
        return result

    def _json_lookup(self, data, key_name, result, one_match):
        """
        recurses through a nested dictionary/list structure till
        it finds a key in a dict, and returns a value.
        If we have to iterate through a list along the way we will
        recurse down each item on the list.
        """
        if one_match and len(result) != 0:
            return

        if isinstance(data, list):
            for entry in data:
                self._json_lookup(entry, key_name, result, one_match)

        elif isinstance(data, dict):
            for k, v in data.items():
                if key_name == k:
                    result.append(data[key_name])
                else:
                    self._json_lookup(v, key_name, result, one_match)

    def _get_neighbors(self, family: Literal[4, 6]):
        """
        aoscx does both ipv4 and ipv6 in the same REST call, so
        it's simpler to write one method for both get_arp_table and
        get_ipv6_neighbors_table and just filter out what we want.

        Note that we don't route any customer networks *on* Aruba -
        this was tested against an edgeless device.
        """
        arp = self._iter_get("system/vrfs", sub_path="neighbors")
        results = []
        for _, neighs in arp.items():
            for _, url in neighs.items():
                neigh = self._get(url)
                ip_obj = netaddr.IPAddress(neigh["ip_address"])
                if (ip_obj.version == 4 and family == 6) or (
                    ip_obj.version == 6 and family == 4
                ):
                    continue
                results.append(
                    {
                        "interface": list(neigh["port"].keys())[0],
                        "mac": neigh["mac"],
                        "ip": neigh["ip_address"],
                        "age": 0,
                    }
                )

        return results

    def get_arp_table(self) -> List[napalm_models.ARPTableDict]:
        return self._get_neighbors(family=4)

    def get_config(
        self, retrieve="all", full=False, sanitized=False, format="text"
    ) -> napalm_models.ConfigDict:
        if sanitized:
            raise NotImplementedError("Sanitized nos config not supported")
        if format not in ["text", "json"]:
            raise NotImplementedError("Only text and json config formats supported")

        # for text format we're going to SSH into the device and do 'show config'
        # in this scenario 'candidate' isn't really relevant.
        config = {"startup": "", "running": "", "candidate": ""}
        if format == "text":
            with self.ssh_conn() as ssh_device:
                config["running"] = ssh_device.send_command("show running-config")
                config["startup"] = ssh_device.send_command("show startup-config")
        else:
            config["running"] = self._get("fullconfigs/running-config")
            config["startup"] = self._get("fullconfigs/startup-config")

        return config

    def get_facts(self) -> napalm_models.FactsDict:
        sys_attrs = [
            "software_version",
            "boot_time",
            "applied_domain_name",
            "applied_hostname",
        ]
        sys_data = self._get("system", attrs=sys_attrs)
        chassis = self._get("system/subsystems/chassis,1", attrs=["product_info"])

        facts = {
            "os_version": sys_data.get("software_version", ""),
            "uptime": sys_data.get("boot_time", 0),
            "interface_list": list(self._get("system/interfaces")),
            "vendor": "Aruba",
            "serial_number": self.json_lookup(chassis, "serial_number"),
            "model": self.json_lookup(chassis, "part_number"),
            "hostname": sys_data.get("applied_hostname", ""),
            "fqdn": sys_data.get("applied_domain_name", ""),
        }

        return facts

    def get_interfaces(self) -> Dict[str, napalm_models.InterfaceDict]:
        """napalm get interfaces"""
        attrs = [
            "admin_state",
            "description",
            "mac_in_use",
            "link_speed",
            "link_state",
            "mtu",
            "link_resets_timestamp",
        ]
        interfaces = self._iter_get("system/interfaces", attrs=attrs)

        output = {}
        for i_name, i_data in interfaces.items():
            output[i_name] = {
                "is_up": i_data["link_state"] == "up",
                "is_enabled": i_data["admin_state"] == "up",
                "description": i_data["description"] if i_data["description"] else "",
                "last_flapped": i_data["link_resets_timestamp"],
                "mtu": i_data["mtu"],
                # speed is in bits and napalm wants megabits
                "speed": i_data["link_speed"] / 1000000
                if i_data["link_speed"]
                else 0.0,
                "mac_address": i_data["mac_in_use"],
            }

        return output

    def get_ipv6_neighbors_table(self) -> List[napalm_models.IPV6NeighborDict]:
        return self._get_neighbors(family=6)

    def get_lldp_neighbors(self) -> Dict[str, List[napalm_models.LLDPNeighborDict]]:
        output = {}
        i_lldp = self._iter_get("system/interfaces", sub_path="lldp_neighbors")

        # lldp endpoint for each interface is itself a path that must be resolved
        # to get more than just the mac address of each neighbor
        for port, neighbors in i_lldp.items():
            for n_path in neighbors.values():
                n_details = self._get(n_path)

                if not output.get(port):
                    output[port] = []

                output[port].append(
                    {
                        "hostname": self.json_lookup(n_details, "chassis_name"),
                        "port": n_details["port_id"],
                    }
                )

        return output

    def get_mac_address_table(self) -> List[napalm_models.MACAdressTable]:
        """napalm get mac address table"""
        output = []
        macs = self._iter_get("system/vlans", sub_path="macs")
        for vlan, v_macs in macs.items():
            if not v_macs:
                continue

            for v_mac, url in v_macs.items():
                attrs = ["mac_addr", "port", "number_of_moves"]
                mac_data = self._get(url, attrs=attrs)
                output.append(
                    {
                        "mac": mac_data["mac_addr"],
                        "interface": list(mac_data["port"].keys())[0],
                        "vlan": int(vlan),
                        "static": "dynamic" not in v_mac,
                        "active": True,
                        "moves": mac_data["number_of_moves"]
                        if mac_data["number_of_moves"]
                        else 0,
                        "last_move": 0,
                    },
                )

        return output

    def get_optics(self) -> Dict[str, napalm_models.OpticsDict]:
        """
        Rest get optics is very slow on the dnoc aristas so
        using ssh instead
        """
        with self.ssh_conn() as ssh_device:
            result = ssh_device.send_command("show interface dom")

            output = {}
            for line in result.split("\n"):
                m = re.match(
                    r"(\d+\/\d+\/\d+)\s+\S+\s+\S+\s+\S+\s+(\S+)\s+(\S+)\s+(\S+)",
                    line,
                )
                if m:
                    i_name = m.group(1)
                    output[i_name] = {"physical_channels": {"channels": {}}}
                    i_channels = output[i_name]["physical_channels"]["channels"]
                    i_channels[0] = {
                        "laser_bias_current": 0.0
                        if m.group(2) == "n/a"
                        else m.group(2),
                        "input_power": 0.0 if m.group(3) == "n/a" else m.group(3),
                        "output_power": 0.0 if m.group(4) == "n/a" else m.group(4),
                    }

            return output

    # def get_optics(self) -> Dict[str, napalm_models.OpticsDict]:
    #     output = {}
    #     interfaces = self._iter_get("system/interfaces", attrs=["pm_monitor"])

    #     for i_name, data in interfaces.items():
    #         i_data = data["pm_monitor"]

    #         if not i_data:
    #             continue

    #         output[i_name] = {"physical_channels": {"channels": {}}}
    #         i_channels = output[i_name]["physical_channels"]["channels"]
    #         for channel, c_data in i_data.items():
    #             if channel == "common":
    #                 continue
    #             i_channels[channel] = {
    #              "input_power": 10 * math.log(c_data["rx_power"]),
    #              "output_power": 10 * math.log(c_data["tx_power"]),
    #              "laser_bias_current": c_data.get("tx_bias", "0.0"),
    #             }

    #     return output

    # def get_optics(self) -> Dict[str, napalm_models.OpticsDict]:
    #     output = {}
    #     interfaces = self._iter_get("system/interfaces", attrs=["pm_info"])
    #     for i_name, data in interfaces.items():
    #         i_data = data["pm_info"]

    #         # if there's no optic installed or optics aren't supported
    #         # skip this port
    #         if i_data.get("connector", "absent") == "absent":
    #             continue

    #         output[i_name] = {"physical_channels": {"channels": {}}}
    #         i_channels = output[i_name]["physical_channels"]["channels"]

    #         # single-channel optics - not sure how multi-channel optics
    #         # look yet
    #         if i_data.get("rx_power"):
    #             i_channels["0"] = {
    #                 "input_power": 10 * math.log(i_data["rx_power"]),
    #                 "output_power": 10 * math.log(i_data["tx_power"]),
    #                 "laser_bias_current": i_data.get("tx_bias", "0.0"),
    #             }

    #     return output

    def get_inventory(self) -> List[models.InventoryDict]:
        output = []
        optics = self._iter_get("system/interfaces", attrs=["pm_info"])

        for i_name, optic in optics.items():
            i_data = optic["pm_info"]

            # if there's no optic installed or optics aren't supported
            # skip this port
            if i_data.get("connector", "absent") == "absent":
                continue

            output.append(
                {
                    "type": "optic",
                    "subtype": i_data.get("xcvr_desc", ""),
                    "name": i_name,
                    "part_number": i_data.get("vendor_part_number", ""),
                    "serial_number": i_data.get("vendor_serial_number", ""),
                }
            )

        return output
