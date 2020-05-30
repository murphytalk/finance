#!/usr/bin/env bash
#https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
set -euo pipefail

if [ ! -L $0 ];then
    echo "Do not run this script directly, make a symlink and name it as action"
    exit 1
fi

sudo -u mu `dirname $0`/run-on-deepwater.sh `basename $0`
