import logging
import os

if os.path.exists("sexybabeycord.log"):    
    os.remove("sexybabeycord.log")

logging.basicConfig(filename='sexybabeycord.log', level=logging.INFO)
logging.info('Started')