#!/bin/sh

export FINANCE_DB=/data/finance.db
export SERVER_HOST=`ifconfig eth0 |grep 'inet addr'|sed 's/.*addr:\(.*\) Bcast.*$/\1/g'`
exec python /finance/src/runserver.py 8080

