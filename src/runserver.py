#!/usr/bin/env python3
"""
This script runs the finance application using a development server.
"""
from sys import argv
from os import environ
from werkzeug.serving import run_simple

from finance import application, DEBUG

if __name__ == '__main__':
    if len(argv) != 2:
        print("need port as parameter")
    else:
        HOST = environ.get('SERVER_HOST', 'localhost')
        try:
            PORT = int(argv[1])
            run_simple(HOST, PORT, application, use_reloader=DEBUG)
        except ValueError:
            print('Come on, gimme a valid integer as port number!')
