
import re
from napalm.base import NetworkDriver
from napalm.base.helpers import textfsm_extractor
from ..base import SCBaseSSHDriver

from pprint import pprint
from copy import deepcopy


class WaveServerDriver(SCBaseSSHDriver, NetworkDriver):

    INVENTORY_TO_TYPE = {
        # note we're using the fact that this dict gets evaluated
        # sequentially to catch the linecards, whose descriptions are varied
        # but all end in 'Module'
        r"Chassis": None, # Not saving chassis in inventory, that should come from get_facts
        r"Control Processor": "re",  # best guess? Idk what these WAN things are
        r"Access Panel": None,  # I think this is a patch panel or cable mgmt?
        r"Power": "psu",  # FEXes in Dearborn
        r"Fan Module": "fan",  # chassis for fixed config Nexus
        r"EDFA": "linecard", # when I google this it feels vaguely linecard-y
        r"SFP": "optic",
    }

    def _get_inventory_subtype(self, entry):
        """
        Inventory subtype is really just for optics models.
        The only optics in the two scimet waveservers look like:
        '400G-FR4, SMF, 2KM QSFP-DD'
        """

        if "SFP" in entry["model"]:
            return entry["model"].split(",")[0]
        return None

    def get_config(self, retrieve="all", full=False, sanitized=False, format="text"):
        """
        Waveserver appears to have one config
        """
        result = {"startup": "", "candidate": "", "running": ""}
        if retrieve in ["all", "running"]:
            result["running"] = self.send_command("configuration show")
        if retrieve in ["all", "startup"]:
            result["startup"] = self.send_command("configuration show")
        return result

    def get_inventory(self):
        """
        Waveserver inventory
        """
        raw_inv = self.send_command("chassis inventory show")
        inv = textfsm_extractor(self, "chassis_inventory_show", raw_inv)

        output = []
        for entry in inv:
            output.append(
                {
                    "type": self._get_inventory_type(entry["model"]),
                    "subtype": self._get_inventory_subtype(entry),
                    "name": entry["unit"],
                    "part_number": entry["pn"],
                    "serial_number": entry["sn"],
                },
            )
        return output
    
    def get_optics(self):
        """
        Need to do 'xcvr show' to get port names then can iterate over
        'xcvr show xcvr X diagnostics'
        """
        raw_xcvrs = self.send_command("xcvr show")
        xcvrs = textfsm_extractor(self, "xcvr_show", raw_xcvrs)
        
        output = {}
        for xcvr in xcvrs:
            i_name = xcvr['port']
            diags_raw = self.send_command(f"xcvr show xcvr {i_name} diagnostics")

            # textfsm templates doesn't like the weird dividers between output rows
            # so we're gonna do our parsing ourselves :(
            i_channels = {"physical_channels": {"channels": []}}
            curr_i = i_channels["physical_channels"]["channels"]

            channel_template = {
                "index": None,
                "state": {
                    "input_power": None,
                    "output_power": None,
                    "laser_bias_current": None,
                    },
            }
            channel = deepcopy(channel_template)
            for line in diags_raw.split("\n"):

                # Start of a new channel
                m = re.match(r"\|\s+(\d+)\s+\|\s+Laser Bias\(mA\)\|\s+([\d\.]+)\s+\|", line)
                if m:

                    # if we have a previous channel entry
                    if channel["index"]:
                        i_channels["physical_channels"]["channels"].append(channel)
                        channel = deepcopy(channel_template)

                    channel["index"] = m.group(1)
                    channel["state"]["laser_bias_current"] = m.group(2)
                    continue

                # Coherent optic with a single channel - no bias current
                m = re.match(r"\|\s+(\d+)\s+\|\s+Tx Power \(dBm\)\|\s+([\-\d\.]+)\s+\|", line)
                if m:
                    channel["index"] = m.group(1)
                    channel["state"]["output_power"] = m.group(2)
                    channel["state"]["laser_bias_current"] = 0.0
                    continue

                # tx power for a channel
                m = re.match(r"\|\s+\|\s+Tx Power \(dBm\)\|\s+([\-\d\.]+)\s+\|", line)
                if m:
                    channel["state"]["output_power"] = m.group(1)
                    continue                

                # rx power for a channel
                m = re.match(r"\|\s+\|\s+Rx Power \(dBm\)\|\s+([\-\d\.]+)\s+\|", line)
                if m:
                    channel["state"]["input_power"] = m.group(1)
                    continue                
            
            # save the last entry
            if channel["index"]:
                i_channels["physical_channels"]["channels"].append(channel)
            
            # save interface to output
            if curr_i:
                output[i_name] = i_channels
            

        return output