#!/usr/bin/env python3
"""
This script runs the finance application using a development server.
"""
from sys import argv
from os import environ
import os
from werkzeug.serving import run_simple

import logging.config

log_conf_file = os.path.dirname(os.path.realpath(__file__)) + "/../logging.conf"
logging.config.fileConfig(log_conf_file )

logger = logging.getLogger(__name__)
logger.info("logger configuration : %s",log_conf_file)


from finance import app, DEBUG

if __name__ == '__main__':
    if len(argv) != 2:
        print("need port as parameter")
    else:
        HOST = environ.get('SERVER_HOST', 'localhost')
        try:
            PORT = int(argv[1])
            run_simple(HOST, PORT, app, use_reloader=DEBUG)
        except ValueError:
            print('Come on, gimme a valid integer as port number!')
