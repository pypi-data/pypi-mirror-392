from netmiko import BaseConnection
from napalm.base import models as napalm_models, NetworkDriver

from ..base import SCBaseSSHDriver


class CienaRLS(SCBaseSSHDriver, NetworkDriver):
    """
	Netmiko-based Ciena RLS SSH driver
    """
    def get_config(
        self, retrieve="all", full=False, sanitized=False, format="text"
    ) -> napalm_models.ConfigDict:
        config = self.send_command("show-config", read_timeout=60)

        return {"startup": {}, "candidate": {}, "running": config}
