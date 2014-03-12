from logging import getLogger, Formatter, DEBUG, StreamHandler

logger = getLogger()
logger.setLevel(DEBUG)

# Log to physical file.

c = StreamHandler()
f = Formatter('%(asctime)s [%(name)s %(levelname)s] %(message)s')
c.setFormatter(f)
logger.addHandler(c)

