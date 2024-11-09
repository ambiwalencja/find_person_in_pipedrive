import logging
import datetime

today = datetime.date.today()

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO) 
f_handler = logging.FileHandler(f'{today}.log')
f_handler.setLevel(logging.INFO)
f_format = logging.Formatter('%(asctime)s - %(process)d - %(name)s - %(levelname)s - %(message)s')
f_handler.setFormatter(f_format)
logger.addHandler(f_handler)
