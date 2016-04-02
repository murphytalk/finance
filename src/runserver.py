#!/usr/bin/python2
"""
This script runs the finance application using a development server.
"""
from os import environ
from werkzeug.serving import run_simple

from finance import application, DEBUG

if __name__ == '__main__':
    HOST = environ.get('SERVER_HOST', 'localhost')
    try:
        PORT = int(environ.get('SERVER_PORT', '5555'))
    except ValueError:
        PORT = 5555

    run_simple(HOST, PORT, application, use_reloader=DEBUG)
