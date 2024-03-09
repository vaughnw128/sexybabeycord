"""
    __init__

    Just handles some logging stuff, mostly

    Made with love and care by Vaughn Woerpel
"""

# built-in
import logging
import os
import sys
from datetime import datetime

# external
import coloredlogs

# project modules
from bot import constants

root_log = logging.getLogger()

format_string = "%(asctime)s - %(levelname)s : [%(module)s] %(message)s"
log_format = logging.Formatter(format_string)

if not os.path.exists(constants.Logging.loglocation):
    os.makedirs(constants.Logging.loglocation)

# Sets file writer
time = str(datetime.now().strftime("%Y%m%d"))
filename = f"sexybabeycord-{time}.log"
file_handler = logging.FileHandler(
    f"{constants.Logging.loglocation}{filename}", encoding="utf8"
)
file_handler.setFormatter(log_format)
root_log.addHandler(file_handler)

# Sets colored logs formatting
coloredlogs.DEFAULT_LEVEL_STYLES = {
    **coloredlogs.DEFAULT_LEVEL_STYLES,
    "trace": {"color": 246},
    "critical": {"background": "red"},
    "debug": coloredlogs.DEFAULT_LEVEL_STYLES["info"],
}
coloredlogs.DEFAULT_LOG_FORMAT = format_string
coloredlogs.install(level=5, logger=root_log, stream=sys.stdout)

# Sets module log levels
root_log.setLevel(logging.INFO)
logging.getLogger("discord").setLevel(logging.WARNING)
logging.getLogger("asyncio").setLevel(logging.INFO)
