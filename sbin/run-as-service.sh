#!/usr/bin/env bash
#https://vaneyckt.io/posts/safer_bash_scripts_with_set_euxo_pipefail/
set -euo pipefail

# for OpenRC
# make symlink /etc/local.d/finance.start and /etc/local.d/finance.stop to this file

if [ ! -L $0 ];then
    echo "Do not run this script directly, make a symlink and name it as action"
    exit 1
fi
realpath=$(readlink $0)
cmd=$(echo `basename $0`|sed -r 's/.*\.(.*)$/\1/g')
sudo -u mu `dirname $realpath`/run-on-deepwater.sh $cmd

