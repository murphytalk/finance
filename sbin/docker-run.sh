#!/bin/sh

export FINANCE_DB=/data/finance.db
export SERVER_HOST='0.0.0.0'
exec python3 /finance/src/runserver.py 8080
