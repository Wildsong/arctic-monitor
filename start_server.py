import sys
import waitress
import os
#from logging.config import fileConfig
#logfile = sys.argv[1]

try:
    myport = os.environ['VIRTUAL_PORT']
except:
    myport=5000

from license_monitor import app
waitress.serve(app, threads=16, host='0.0.0.0', port=myport)
