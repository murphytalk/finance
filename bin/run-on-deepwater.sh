#!/usr/bin/env bash
#
. /mnt/extra/run/finance-venv/bin/activate
export FINANCE_DB=/home/mu/Dropbox/data/finance.db
`dirname $0`/run.sh "$@"
