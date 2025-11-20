# from .iosxr_netconf import SCIOSXR
from .iosxr import SCIOSXR_SSH
from .iosxr_netconf import SCIOSXR
from .junos import SCJunOS
from .nxos import SCNXOS
from .sros import SCNokiaSROSDriver
from .srl import SCNokiaSRLDriver
from .eos import SCEOSDriver
from .nos import SCNOSDriver
from .aoscx import SCAOSCXDriver
from .waveserver import WaveServerDriver
from .psimn import PSIMN
from .rls import CienaRLS
from .saos import SCCienaSAOS

PLATFORM_MAP = {
    "iosxr": SCIOSXR_SSH,
    "iosxr_netconf": SCIOSXR,
    "nxos": SCNXOS,
    "junos": SCJunOS,
    "sros": SCNokiaSROSDriver,
    "srl": SCNokiaSRLDriver,
    "eos": SCEOSDriver,
    "nos": SCNOSDriver,
    "waveserver": WaveServerDriver,
    "aoscx": SCAOSCXDriver,
    "psimn": PSIMN,
    "rls": CienaRLS,
    "saos": SCCienaSAOS,
}


def get_network_driver(platform: str):
    """
    Returns network driver based on platform string.
    """
    for valid_platform, driver in PLATFORM_MAP.items():
        if valid_platform == platform:
            return driver

    raise NotImplementedError(f"Unsupported platform {platform}")
