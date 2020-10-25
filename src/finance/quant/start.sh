#!/usr/bin/env bash
set -euo pipefail

NOTEBOOKS_PROJ=${HOME}/work/jupyter-notebooks

if [ ! -d $NOTEBOOKS_PROJ ];then
    echo Checkout out github.com:murphytalk/jupyter-notebooks.git to $NOTEBOOKS_PROJ first
    exit 1
fi

source $NOTEBOOKS_PROJ/shared.inc
build_image finance `pwd`/docker
start_container finance finance-vm 8888 /home/jovyan/work
