#!/usr/bin/env bash
export FINANCE_DB=${HOME}/Dropbox/data/finance.db
export VENV=${HOME}/work/finance/v
`dirname $0`/run.sh "$@"
