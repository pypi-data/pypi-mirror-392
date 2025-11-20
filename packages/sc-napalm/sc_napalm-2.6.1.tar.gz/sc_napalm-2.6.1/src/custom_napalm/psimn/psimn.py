from netmiko import BaseConnection
from napalm.base import models as napalm_models, NetworkDriver

from ..base import SCBaseSSHDriver


class PSIMN(SCBaseSSHDriver, NetworkDriver):
    """
        Very sketchy, basic driver for noc-wan-nokia-psi-dc
        running 1830PSIMN-25.6-0 to pull config backups.

    Netmiko doesn't appear to model this so we're
    doing a paramiko-based driver instead.
    """

    def open(self):
        """
        Implementation of NAPALM method 'open' to open a connection to the device.
        """
        SCBaseSSHDriver.open(self)

        # switching to a different CLI that we know how to run commands
        self.device.send_command(
            "//\n", expect_string="Switching to MD-CLI", cmd_verify=False
        )

    def get_config(
        self, retrieve="all", full=False, sanitized=False, format="text"
    ) -> napalm_models.ConfigDict:
        config = self.send_command("admin show running | no-more")

        return {"startup": {}, "candidate": {}, "running": config}
