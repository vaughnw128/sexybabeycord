""" __init__ file, just handles logging """

import coloredlogs
import logging
import os
import sys
from bot import constants

if os.path.exists(constants.Logging.logfile):    
    os.remove(constants.Logging.logfile)

root_log = logging.getLogger()

format = "%(asctime)s - %(levelname)s : [%(module)s] %(message)s"
log_format = logging.Formatter(format)

# Sets file writer
file_handler = logging.FileHandler(constants.Logging.logfile, encoding="utf8")
file_handler.setFormatter(log_format)
root_log.addHandler(file_handler)

# Sets colored logs formatting
coloredlogs.DEFAULT_LEVEL_STYLES = {
        **coloredlogs.DEFAULT_LEVEL_STYLES,
        "trace": {"color": 246},
        "critical": {"background": "red"},
        "debug": coloredlogs.DEFAULT_LEVEL_STYLES["info"]
    }
coloredlogs.DEFAULT_LOG_FORMAT = format
coloredlogs.install(level=5, logger=root_log, stream=sys.stdout)

# Sets module loglevels
root_log.setLevel(logging.INFO)
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.INFO)