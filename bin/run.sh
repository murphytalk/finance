#!/bin/bash

FINANCE_DB=`find $HOME -type f -name finance.db`

if [ -z "$FINANCE_DB" ];then
	echo Cannot find finance.db !
	exit 1
fi

export FINANCE_DB
export SERVER_PORT=8080

CUR=`dirname $0`
LOG=$CUR/../log
LOGF=${LOG}/run.`date +%Y%m%d`.log
PIDF=${LOG}/run.pid
cmd=$1

[ -z "$cmd" ] && cmd=status
[ -d $LOG ] || mkdir -p $LOG


check_status(){
	status=0
	if [ -f $PIDF ];then
		if ps `cat $PIDF` > /dev/null;then
			status=1
		fi
	fi
}

report_status(){
	check_status
	if [ $status -eq 0 ];then
		echo Not running 
	else
		echo Running
	fi
} 


case $cmd in
start)
	check_status
	if [ $status -eq 0 ];then
		echo DB file is $FINANCE_DB
		nohup ${CUR}/runserver.py > $LOGF 2>&1 &
		echo $! > $PIDF
	else
		echo Already started!
	fi	
	;;
stop)
	if [ -f $PIDF ];then
		kill -9 `cat $PIDF`
		rm -f $PIDF
	else
		echo PID file does not exist ... use regex to kill
		
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
