from napalm_srl import NokiaSRLDriver
from napalm_srl.srl import SRLAPI
from napalm.base import models as napalm_models
from ..base import SCBaseNetconfDriver

from ipaddress import IPv6Address

from napalm.base.helpers import convert

import logging


class SCSLRAPI(SRLAPI):
    """
    This override fixes an issue with IPv6 addresses embedded in URLs when talking
    over GRPCs.
    """

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        super().__init__(hostname, username, password, timeout, optional_args)

        try:
            IPv6Address(hostname)
            self.target = f"[{hostname}]:{self.gnmi_port}"
        except ValueError:
            pass


class SCNokiaSRLDriver(NokiaSRLDriver, SCBaseNetconfDriver):
    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """
        Forcing insecure connection for testing purposes
        """
        optional_args = optional_args if optional_args else {}
        optional_args["insecure"] = True
        optional_args["skip_verify"] = True

        optional_args["encoding"] = "JSON_IETF"

        super().__init__(
            hostname, username, password, timeout=timeout, optional_args=optional_args
        )

        self.device = SCSLRAPI(
            hostname, username, password, timeout=timeout, optional_args=optional_args
        )

    def get_interfaces(self):
        """
        Nokia driver returns interface speeds at Gbps and not Mbps which is
        wrong.
        """
        results = super().get_interfaces()
        for i_name in results.keys():
            if results[i_name]["speed"] != -1:
                results[i_name]["speed"] = 1000 * results[i_name]["speed"]

        return results

    def get_config(
        self, retrieve="all", full=False, sanitized=False, format="text"
    ) -> napalm_models.ConfigDict:
        """
        pulling running config via ssh sow we can have it in 'display set' format.
        """
        if format != "text":
            return super().get_config(
                retrieve=retrieve, full=full, sanitized=sanitized, format=format
            )

        config = {"startup": "", "running": "", "candidate": ""}

        with self.ssh_conn() as ssh_device:
            if retrieve in ["all", "running"]:
                config["running"] = ssh_device.send_command("info from running flat")
            if retrieve in ["all", "startup"]:
                config["startup"] = ssh_device.send_command("info from startup flat")
            if retrieve in ["all", "candidate"]:
                config["candidate"] = ssh_device.send_command(
                    "info from candidate flat"
                )

        return config

    def get_optics(self):
        path = {"/interface"}
        path_type = "STATE"
        output = self.device._gnmiGet("", path, path_type)
        interfaces = self._getObj(
            output, *["srl_nokia-interfaces:interface"], default=[]
        )
        channel_data = {}

        for i in interfaces:
            if not self._getObj(i, *["transceiver", "channel"], default=False):
                continue

            name = self._getObj(i, *["name"])
            channel = self._getObj(i, *["transceiver", "channel"], default={})[0]
            channel_data.update(
                {
                    name: {
                        "physical_channels": {
                            "channel": [
                                {
                                    "index": self._getObj(
                                        channel, *["index"], default=-1
                                    ),
                                    "state": {
                                        "input_power": {
                                            "instant": self._getObj(
                                                channel,
                                                *["input-power", "latest-value"],
                                                default=-1.0,
                                            ),
                                            "avg": -1.0,
                                            "min": -1.0,
                                            "max": -1.0,
                                        },
                                        "output_power": {
                                            "instant": self._getObj(
                                                channel,
                                                *["output-power", "latest-value"],
                                                default=-1.0,
                                            ),
                                            "avg": -1.0,
                                            "min": -1.0,
                                            "max": -1.0,
                                        },
                                        "laser_bias_current": {
                                            "instant": self._getObj(
                                                channel,
                                                *["laser-bias-current", "latest-value"],
                                                default=-1.0,
                                            ),
                                            "avg": -1.0,
                                            "min": -1.0,
                                            "max": -1.0,
                                        },
                                    },
                                }
                            ]
                        }
                    }
                }
            )

        return channel_data

    def get_inventory(self):
        path = {"/interface/transceiver"}
        path_type = "STATE"
        output = self.device._gnmiGet("", path, path_type)
        transceivers = self._getObj(
            output, *["srl_nokia-interfaces:interface"], default=[]
        )
        result = []
        for t_if in transceivers:
            trans = t_if["transceiver"]

            if "serial-number" not in trans:
                continue

            result.append(
                {
                    "type": "optic",
                    "subtype": trans["ethernet-pmd"],
                    "name": t_if["name"],
                    "part_number": trans["vendor-part-number"],
                    "serial_number": trans["serial-number"],
                }
            )

        return result

    def get_arp_table(self, vrf=""):
        """
        Copied from the community driver, which has a bug in
        the 'vrf_path' statements
        """

        try:
            arp_table = []
            subinterface_names = []

            def _find_neighbors(is_ipv4, ip_dict):
                ip_dict = eval(ip_dict.replace("'", '"'))
                neighbor_list = self._find_txt(ip_dict, "neighbor")
                if neighbor_list:
                    neighbor_list = list(eval(neighbor_list))
                    for neighbor in neighbor_list:
                        ipv4_address = ""
                        ipv6_address = ""
                        timeout = -1.0
                        reachable_time = -1.0
                        if is_ipv4:
                            ipv4_address = self._find_txt(neighbor, "ipv4-address")
                            timeout = convert(
                                float, self._find_txt(ip_dict, "timeout"), default=-1.0
                            )
                        else:
                            ipv6_address = self._find_txt(neighbor, "ipv6-address")
                            reachable_time = convert(
                                float,
                                self._find_txt(ip_dict, "reachable-time"),
                                default=-1.0,
                            )
                        arp_table.append(
                            {
                                "interface": sub_interface_name,
                                "mac": self._find_txt(neighbor, "link-layer-address"),
                                "ip": ipv4_address if is_ipv4 else ipv6_address,
                                "age": timeout if is_ipv4 else reachable_time,
                            }
                        )

            if vrf:
                vrf_path = {"network-instance[name={}]/interface".format(vrf)}
            else:
                vrf_path = {"network-instance[name=*]/interface"}
            pathType = "STATE"

            vrf_output = self.device._gnmiGet("", vrf_path, pathType)
            if not vrf_output:
                return []
            for vrf in vrf_output["srl_nokia-network-instance:network-instance"]:
                if "interface" in vrf.keys():
                    subinterface_list = self._find_txt(vrf, "interface")
                    subinterface_list = list(eval(subinterface_list))
                    for dictionary in subinterface_list:
                        if "name" in dictionary.keys():
                            subinterface_names.append(
                                self._find_txt(dictionary, "name")
                            )

            interface_path = {"interface[name=*]"}
            interface_output = self.device._gnmiGet("", interface_path, pathType)

            for interface in interface_output["srl_nokia-interfaces:interface"]:
                interface_name = self._find_txt(interface, "name")
                if interface_name:
                    sub_interface = self._find_txt(interface, "subinterface")
                    if sub_interface:
                        sub_interface = list(eval(sub_interface))
                        for dictionary in sub_interface:
                            sub_interface_name = self._find_txt(dictionary, "name")
                            if sub_interface_name in subinterface_names:
                                ipv4_data = self._find_txt(dictionary, "ipv4")
                                if ipv4_data:
                                    ipv4_data = eval(ipv4_data.replace("'", '"'))
                                    ipv4_arp_dict = self._find_txt(
                                        ipv4_data, "srl_nokia-interfaces-nbr:arp"
                                    )
                                    if ipv4_arp_dict:
                                        _find_neighbors(True, ipv4_arp_dict)

                                ipv6_data = self._find_txt(dictionary, "ipv6")
                                if ipv6_data:
                                    ipv6_data = eval(ipv6_data.replace("'", '"'))
                                    ipv6_neighbor_dict = self._find_txt(
                                        ipv6_data,
                                        "srl_nokia-if-ip-nbr:neighbor-discovery",
                                    )
                                    if ipv6_neighbor_dict:
                                        _find_neighbors(False, ipv6_neighbor_dict)
            return arp_table
        except Exception as e:
            logging.error("Error occurred : {}".format(e))
