import logging.config
import logging

# create logger
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', datefmt='%Y/%m/%d %I:%M:%S %p',
                    filename='r1mmensageria.log', level=logging.INFO)
logger = logging.getLogger('Rede1Minuto Server')

# create console handler and set level to debug
ch = logging.StreamHandler()
ch.setLevel(logging.INFO) 

# create formatter
formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
ch.setFormatter(formatter)

# add ch to logger
logger.addHandler(ch)
