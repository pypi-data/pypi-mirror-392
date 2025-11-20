from typing import Dict, List, Optional
import re
from napalm.base import models as napalm_models
from netmiko.ssh_dispatcher import ConnectHandler, CLASS_MAPPER_BASE
from netmiko import BaseConnection

from . import models as sc_models


class SCBaseDriver:
    """
    Base class that all children should inherit
    """

    # populate in child classes
    INVENTORY_TO_TYPE = {}

    def _get_inventory_type(self, name: str) -> str:
        """
        Maps the name of the inventory item to its type
        """
        for pattern, inv_type in self.INVENTORY_TO_TYPE.items():
            if inv_type and inv_type not in sc_models.VALID_INVENTORY_TYPES.__args__:
                raise TypeError(f"Invalid Inventory type {inv_type}")
            if re.search(pattern, name):
                return inv_type

        raise ValueError(f"Unknown inventory item {name}")

    def get_ipv6_neighbors_table(self) -> List[napalm_models.IPV6NeighborDict]:
        raise NotImplementedError

    def get_arp_table(self) -> List[napalm_models.ARPTableDict]:
        """napalm get arp table"""
        raise NotImplementedError

    def get_config(self) -> napalm_models.ConfigDict:
        """napalm get config"""
        raise NotImplementedError

    def get_facts(self) -> napalm_models.FactsDict:
        """napalm get facts"""
        raise NotImplementedError

    def get_lldp_neighbors(self) -> Dict[str, List[napalm_models.LLDPNeighborDict]]:
        """napalm get lldp neighbors"""
        raise NotImplementedError

    def get_interfaces(self) -> Dict[str, napalm_models.InterfaceDict]:
        """ " napalm get interfaces"""
        raise NotImplementedError

    def get_inventory(self) -> List[sc_models.InventoryDict]:
        """sc get inventory"""
        raise NotImplementedError

    def get_mac_address_table(self) -> List[napalm_models.MACAdressTable]:
        """napalm get mac address table"""
        raise NotImplementedError

    def get_optics(self) -> Dict[str, napalm_models.OpticsDict]:
        """napalm get optics"""
        raise NotImplementedError


class SCBaseNetconfDriver(SCBaseDriver):
    """
    Inclues some helper xml functions
    """

    netmiko_host_type = "linux"

    def ssh_conn(self) -> ConnectHandler:
        """
        Ugly workaround for getting stuff via the cli over ssh.
        Starts a netmiko ssh connection handler and returns it,
        allowing you to interact with the CLI of the device.
        """
        optional_args = {}
        if getattr(self, "optional_args", False):
            optional_args = self.optional_args if self.optional_args else {}

        args = {
            "device_type": self.netmiko_host_type,
            "host": self.hostname,
            "username": self.username,
            "password": self.password,
            "ssh_config_file": optional_args.get("ssh_config", None),
        }
        return ConnectHandler(**args)

    def _find_txt(self, xml_tree, path, default=None, namespaces=None):
        """
        Stolen from the napalm iosxr driver
        Extract the text value from a leaf in an XML tree using XPath.

        Will return a default value if leaf path not matched.
        :param xml_tree:the XML Tree object. <type'lxml.etree._Element'>.
        :param path: XPath to be applied in order to extract the desired data.
        :param default:  Value to be returned in case of a no match.
        :param namespaces: namespace dictionary.
        :return: a str value or None if leaf path not matched.
        """
        value = None
        xpath_applied = xml_tree.xpath(path, namespaces=namespaces)

        if xpath_applied:
            if not len(xpath_applied[0]):
                if xpath_applied[0].text is not None:
                    value = xpath_applied[0].text.strip()
                else:
                    value = ""
        else:
            value = default

        return value

    # Helper xml methods that always pass in our namespaces by default
    def _text(self, xml_tree, path, default=None):
        return self._find_txt(xml_tree, path, default, namespaces=self.NS)

    def _xpath(self, xml_tree, path):
        return getattr(xml_tree, "xpath")(path, namespaces=self.NS)

    def _find(self, xml_tree, element):
        return getattr(xml_tree, "find")(element, namespaces=self.NS)

    def _iterfind(self, xml_tree, element):
        return getattr(xml_tree, "iterfind")(element, namespaces=self.NS)


class SCBaseSSHDriver(SCBaseDriver):
    """
    Generic base netmiko driver for all the weird WAN platforms.
    """
    netmiko_host_type = None # set in child class if applicable

    def __init__(
        self,
        hostname: str,
        username: str,
        password: str,
        timeout: int = 60,
        optional_args: Optional[Dict] = None,
    ) -> None:
        if optional_args is None:
            optional_args = {}
        self.hostname = hostname
        self.username = username
        self.password = password
        self.timeout = timeout

    def open(self):
        
        if CLASS_MAPPER_BASE.get(self.netmiko_host_type):
            self.device = self._netmiko_open(self.netmiko_host_type)
        else:
            self.device = BaseConnection(
            ip=self.hostname,
            username=self.username,
            password=self.password,
            timeout=self.timeout,
            
        )

    def close(self):
        self._netmiko_close()

    def send_command(self, cmd: str, read_timeout:int=10) -> str:
        """
        Sends command with netmiko and returns the result
        """
        return self.device.send_command(cmd, read_timeout=read_timeout)