from typing import List
from napalm.eos import EOSDriver
from napalm.base import models as napalm_models
from netaddr import EUI, mac_unix_expanded
import re

from ..base import SCBaseDriver
from ..models import InventoryDict

from pprint import pprint


class SCEOSDriver(EOSDriver, SCBaseDriver):
    ("fabric_module",)
    ("fan",)
    ("linecard",)
    ("optic",)
    ("psu",)
    ("re",)
    ("stack_cable",)
    ("stack_member",)
    ("uplink_module",)
    ("aoc",)
    ("dac",)

    INVENTORY_TO_TYPE = {
        r"Fabric": "fabric_module",
        r"Linecard": "linecard",
        r"Supervisor": "re",
    }

    def __init__(self, hostname, username, password, timeout=60, optional_args=None):
        """
        Forcing ssh transport since we don't enable the web interface
        """
        optional_args = optional_args if optional_args else {}
        optional_args["transport"] = "ssh"

        super().__init__(
            hostname, username, password, timeout=timeout, optional_args=optional_args
        )


    def get_inventory(self) -> List[InventoryDict]:

        output = self._run_commands(["show inventory", "show interface transceiver"], encoding="json")
        inventory = output[0]

        # 'show int transciever' gives us a mapping of the slot number that shows up
        # in 'show inventory' to the name of the interface.
        trans = output[1]["interfaces"]

        slot_to_port = {}
        for i_name, item in trans.items():
            print(f"processing {i_name}")
            if not item:
                continue
            slot = item["slot"].replace("Ethernet","")
            if slot not in slot_to_port:
                slot_to_port[slot] = i_name
        results = []

        ### optics
        for slot, optic in inventory["xcvrSlots"].items():
            if optic.get("modelName"):
                results.append(
                    {
                        "type": "optic",
                        "subtype": optic["modelName"],
                        "name": slot_to_port[slot],
                        "part_number": optic["modelName"],
                        "serial_number": optic["serialNum"],
                    },
                )

        ### line cards
        for slot, card in inventory["cardSlots"].items():
            if card.get("serialNum"):
                results.append(
                    {
                        "type": self._get_inventory_type(slot),
                        "subtype": card["modelName"],
                        "name": f"Ethernet{slot}",
                        "part_number": card["modelName"],
                        "serial_number": card["serialNum"],
                    },
                )

        ### PSUs
        for slot, psu in inventory["powerSupplySlots"].items():
            if psu.get("serialNum"):
                results.append(
                    {
                        "type": "psu",
                        "subtype": None,
                        "name": f"PSU {slot}",
                        "part_number": psu["name"],
                        "serial_number": psu["serialNum"],
                    },
                )

        ### FANs
        for slot, fan in inventory["fanTraySlots"].items():
            if fan.get("serialNum"):
                results.append(
                    {
                        "type": "fan",
                        "subtype": None,
                        "name": f"FAN {slot}",
                        "part_number": fan["name"],
                        "serial_number": fan["serialNum"],
                    },
                )
        return results

    def get_ipv6_neighbors_table(self) -> List[napalm_models.IPV6NeighborDict]:
        """
        Not implemented in Napalm base EOS!
        """
        output = []
        neighbors = self._run_commands(["show ipv6 neighbors vrf all"], encoding="json")
        if not neighbors:
            return output

        for _, vrf in neighbors[0]["vrfs"].items():
            for entry in vrf["ipV6Neighbors"]:
                mac = EUI(entry["hwAddress"])
                mac.dialect = mac_unix_expanded
                output.append(
                    {
                        "interface": entry["interface"],
                        "mac": str(mac),
                        "ip": entry["address"],
                        "age": entry["age"],
                        "state": "REACH",
                    }
                )
        return output

    def get_optics(self):
        """
        napalm eos driver is problematic in several ways so we get to rewrite it
        """
        command = ["show interfaces transceiver"]

        output = self._run_commands(command, encoding="json")[0]["interfaces"]

        # Formatting data into return data structure
        optics_detail = {}

        for port, port_values in output.items():
            if not port_values:
                continue

            # multi-channel optics show up as separate ports, eg
            # Ethernet45/1, Ethernet45/2, Ethernet45/3. We're going to
            # use the 'slot' attribute instead
            port_name = port_values["slot"] + "/1"
            if port_name not in optics_detail:
                optics_detail[port_name] = {"physical_channels": {"channel": []}}

            # Defaulting avg, min, max values to 0.0 since device does not
            # return these values
            optic_states = {
                "index": port_values["channel"],
                "state": {
                    "input_power": {
                        "instant": (
                            port_values["rxPower"] if "rxPower" in port_values else 0.0
                        ),
                        "avg": 0.0,
                        "min": 0.0,
                        "max": 0.0,
                    },
                    "output_power": {
                        "instant": (
                            port_values["txPower"] if "txPower" in port_values else 0.0
                        ),
                        "avg": 0.0,
                        "min": 0.0,
                        "max": 0.0,
                    },
                    "laser_bias_current": {
                        "instant": (
                            port_values["txBias"] if "txBias" in port_values else 0.0
                        ),
                        "avg": 0.0,
                        "min": 0.0,
                        "max": 0.0,
                    },
                },
            }

            optics_detail[port_name]["physical_channels"]["channel"].append(
                optic_states
            )

        return optics_detail
