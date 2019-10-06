#!/usr/bin/env python3
"""
This script runs the finance application using a development server.
"""
from sys import argv
from os import environ, path
from werkzeug.serving import run_simple
from finance import app, DEBUG

import logging.config

log_conf_file = path.dirname(path.realpath(__file__)) + "/../logging.conf"
logging.config.fileConfig(log_conf_file)

logger = logging.getLogger(__name__)
logger.info("logger configuration : %s", log_conf_file)


if __name__ == '__main__':
    if len(argv) != 2:
        print("need port as parameter")
    else:
        HOST = environ.get('SERVER_HOST', 'localhost').strip()
        try:
            PORT = int(argv[1])
            print("running on [{}:{}]".format(HOST, PORT))
            run_simple(HOST, PORT, app, use_reloader=DEBUG)
        except ValueError:
            print('Come on, gimme a valid integer as port number!')
