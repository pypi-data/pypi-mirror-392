from napalm.base import models as napalm_models, NetworkDriver
import re
from copy import deepcopy
from ..base import SCBaseSSHDriver

class SCCienaSAOS(SCBaseSSHDriver, NetworkDriver):
    """
    Community SAOS driver is very old and wants you to have py23_compat.
    Also they don't have get_optics. Also their get_config no longer works.
    So we are writing our own.
    """
    netmiko_host_type = "ciena_saos10"
    _xcvr_ids = None # place to cache xcvr list

    @property
    def xcvr_ids(self):
        """
        Runs 'show xcvrs' and caches them in an internal
        list so we don't have to run this command multiple
        times for multiple getters
        """
        if not self._xcvr_ids:
            self._xcvr_ids = []
            xcvrs = self.send_command("show xcvrs")
            for line in xcvrs.split("\n"):

                m = re.search(r'\| (\d+)\s+\| (enabled|disabled)', line)
                if m:
                    self._xcvr_ids.append(m.group(1))
                    continue

        return self._xcvr_ids

    def get_config(self, retrieve='all'):

        configs = {
            'startup': '',
            'running': '',
            'candidate': '',
        }

        if retrieve in ('running', 'all'):
            output = self.send_command("show running config")
            configs['running'] = output
        if retrieve in ('candidate', 'all'):
            output = self.send_command("show candidate config")
            configs['candidate']

        return configs

    def get_optics(self):
        """
        Again we're in a sad place where we can't use textfsm templates
        because of the output of the data
        """

        i_channels = {"physical_channels": {"channel": []}}

        channel_template = {
            "index": None,
            "state": {
                "input_power": None,
                "output_power": None,
                "laser_bias_current": None,
                },
        }

        value_map = {
            "Tx Power": "output_power",
            "Rx Power": "input_power",
            "Tx Laser Bias": "laser_bias_current",
        }
        output = {}

        for xcvr_id in self.xcvr_ids:
            i_channels = {"physical_channels": {"channel": []}}
            channel = deepcopy(channel_template)
            next_value = None

            diags = self.send_command(f"show xcvr diagnostics xcvr {xcvr_id}")
            for line in diags.split("\n"):

                # Start of a new channel
                m = re.match(r"\|\s+Lane Number\s+\| (\d+)\s+\|", line)
                if m:

                    # if we have a previous channel entry save it
                    if channel["index"]:
                        i_channels["physical_channels"]["channel"].append(channel)
                        channel = deepcopy(channel_template)

                    channel["index"] = m.group(1)
                    continue

                # tx/rx power and bias all have distinct headers on previous rows
                # so we have to flag them to catch them on the next row
                m = re.match(r'\|\s+(Rx Power|Tx Power|Tx Laser Bias)', line)
                if m:
                    next_value = m.group(1)
                
                # actual value is just on a line labeled 'current'
                m = re.match(r"\|\s+Current\s+\| ([\d\.\-]+)\s+\|", line)
                if m and next_value:
                    channel["state"][value_map[next_value]] = m.group(1)
                    next_value = None
      
            
            # save the last entry
            if channel["index"]:
                i_channels["physical_channels"]["channel"].append(channel)
            
            output[xcvr_id] = i_channels
        
        return output
    
    def get_inventory(self):
        """
        For now just getting optics values
        """
        output = []
        entry_template = {
                "type": "optic",
                "subtype": "",
                "name": "",
                "part_number": "",
                "serial_number": "",
        }
        value_map = {
            "Vendor PN": "part_number",
            "Vendor Serial Number": "serial_number",
            "Identifier": "subtype",
        }

        for xcvr in self.xcvr_ids:
            inv = self.send_command(f"show xcvrs xcvr {xcvr}")
            entry = deepcopy(entry_template)

            entry["name"] = xcvr

            for line in inv.split("\n"):

                m = re.match(r"\|\s+(Vendor PN|Vendor Serial Number|Identifier)\s+\| (\S+)", line)
                if m:
                    entry[value_map[m.group(1)]] = m.group(2)
                    continue

            output.append(entry)
        
        return output