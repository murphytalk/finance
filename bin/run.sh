#!/usr/bin/env bash

[ -z "$FINANCE_DB" ] &&  FINANCE_DB=`find $HOME -type f -name finance.db`

if [[ -z "$FINANCE_DB" || ! -f $FINANCE_DB ]];then
	echo Cannot find finance.db !
	exit 1
fi

export FINANCE_DB
SERVER_PORT=8080

CUR=`dirname $0`
SRC=$CUR/../src
LOG=$CUR/../log
LOGF=${LOG}/run.log
cmd=$1

[ -z "$cmd" ] && cmd=status
[ -d $LOG ] || mkdir -p $LOG

CMDSTR="python.*runserver.*${SERVER_PORT}"

check_status(){
	finance_pid=$(ps x | grep $CMDSTR | grep -v grep | awk '{print $1}')
}

report_status(){
	check_status
	if [ -z "$finance_pid" ];then
		echo "Finance portal is NOT running"
	else
		echo "Finance portal (PID=${finance_pid}) is running, finance db is $FINANCE_DB"
	fi
}


case $cmd in
start)
	check_status
	if [ -z "$finance_pid" ];then
		echo "Starting finance portal by using data @ $FINANCE_DB"
		echo "Starting finance portal by using data @ $FINANCE_DB" > $LOGF
		nohup python ${SRC}/runserver.py ${SERVER_PORT} >> $LOGF 2>&1 &
	else
		echo "Finance portal already started!"
	fi
	;;
stop)
	check_status
	if [ -z "$finance_pid" ];then
		echo "Finance portal already stopped"
	else
		kill -9 $finance_pid
	fi
	;;
status)
	report_status
	;;
*)
	report_status
	;;
esac

#remove old log files
find $LOG -type f -name "*.log" -ctime +5 -exec rm  {} \;
