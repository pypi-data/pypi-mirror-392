from typing import Union
import logging
import sys
import argparse
from decouple import config
from os import getenv

LOG_LEVELS = {
    "DEBUG": logging.DEBUG,
    "INFO": logging.INFO,
    "WARNING": logging.WARNING,
    "ERROR": logging.WARNING,
    "CRITICAL": logging.CRITICAL,
}
LOG_FORMAT = "%(asctime)-15s  %(levelname)8s %(name)s %(message)s"


def configure_logging(
    log_level: Union[int, str],
    log_globally: bool = False,
    log_file: str = None,
    log_to_console: bool = False,
):
    """
    Configures logging for the module, or globally as indicated by the input
    """

    if log_globally:
        logger = logging.getLogger()
    else:
        module_name = __name__.split(".")[0]
        logger = logging.getLogger(module_name)

    if isinstance(log_level, str):
        log_level = LOG_LEVELS[log_level.upper()]
    logger.setLevel(log_level)

    if log_file:
        file_handler = logging.handlers.RotatingFileHandler(
            log_file, maxBytes=1024 * 1024 * 10, backupCount=20
        )
        file_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(file_handler)

    if log_to_console:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(stdout_handler)


def get_from_args_or_env(
    cli_arg: str, parsed_args: argparse.Namespace = None, required=True
) -> str:
    """
    Pull a value from parsed arparse, if it's not there look for it
    in .env, and if it's not there, check the user's environment.
    """
    cli_arg = cli_arg.replace("-", "_")

    if getattr(parsed_args, cli_arg, False):
        return getattr(parsed_args, cli_arg)

    env_arg = cli_arg.upper()
    if config(env_arg, None):
        return config(env_arg)

    if getenv(env_arg):
        return getenv(env_arg)

    if required:
        raise ValueError(
            f"ERROR: Please provide {cli_arg} as cli input or set as {env_arg} environment variable"
        )
    return None


def age_to_integer(age: str) -> Union[int, None]:
    """
    Across platforms age strings can be:
    10y5w, 5w4d, 05d04h, 01:10:12, 3w4d 01:02:03,
    50 days 10 hours (ASA)
    """

    # convert empty string to none
    if age == "":
        return None

    # integer age is seconds - we don't need further parsing
    # if we got an integer value
    m = re.search(r"^\d+$", age)
    if m:
        return int(age)

    # Extracting digits out of different time strings
    TIME_MATCHES = [
        r"(?P<hours>\d+):(?P<minutes>\d+):(?P<seconds>\d+)",
        r"(?P<years>\d+) years?",
        r"(?P<months>\d+) months?",
        r"(?P<weeks>\d+) weeks?",
        r"(?P<days>\d+) days?",
        r"(?P<hours>\d+) hours?",
        r"(?P<minutes>\d+) minutes?",
        r"(?P<years>\d+)y",
        r"(?P<weeks>\d+)w",
        r"(?P<days>\d+)d",
        r"(?P<hours>\d+)h",
    ]
    # Multipliers for different units
    UNIT_TO_SECONDS = {
        "years": 31536000,
        "months": 2628000,
        "weeks": 604800,
        "days": 86400,
        "hours": 3600,
        "minutes": 60,
        "seconds": 1,
    }

    seconds = 0

    # search for every time match regex. If  a match is found
    # extract data, apply multiplier, and add to our seconds total
    for match in TIME_MATCHES:
        m = re.search(match, age)
        if not m:
            continue

        for unit, multiplier in UNIT_TO_SECONDS.items():
            if unit in m.groupdict():
                seconds += int(m.groupdict()[unit]) * multiplier

    return seconds
