#!/usr/bin/env bash

[ -z "$FINANCE_DB" ] &&  FINANCE_DB=`find $HOME -type f -name finance.db`

if [[ -z "$FINANCE_DB" || ! -f $FINANCE_DB ]];then
	echo Cannot find finance.db !
	exit 1
fi

export FINANCE_DB
SERVER_PORT=8080
DEMO_PORT=8081

CUR=`dirname $0`
SRC=$CUR/../src
LOG=$CUR/../log
LOGF=${LOG}/run.`date +%Y%m%d`.log
PIDF=${LOG}/run.pid
DEMO_LOGF=${LOG}/run.demo.`date +%Y%m%d`.log
DEMO_PIDF=${LOG}/run.demo.pid
cmd=$1

[ -z "$cmd" ] && cmd=status
[ -d $LOG ] || mkdir -p $LOG


check_status(){
	status=0
	if [ -f $PIDF ];then
		if ps `cat $PIDF` |grep "python.*runserver.*${SERVER_PORT}" > /dev/null;then
			status=`cat $PIDF`
		fi
	fi

	demo_status=0
	if [ -f $DEMO_PIDF ];then
		if ps `cat $DEMO_PIDF` |grep "python.*runserver.*${DEMO_PORT}"> /dev/null;then
			demo_status=`cat $DEMO_PIDF`
		fi
	fi
}

report_status(){
	check_status
	if [ $status -eq 0 ];then
		echo "Finance portal is NOT running"
	else
		echo "Finance portal (PID=${status}) is running"
	fi

	if [ $demo_status -eq 0 ];then
		echo "Finance demo is NOT running"
	else
		echo "Finance demo (PID=${demo_status}) is running"
	fi
} 


case $cmd in
start)
	check_status
	if [ $status -eq 0 ];then
		echo "Starting finance portal by using data @ $FINANCE_DB"
		nohup ${SRC}/runserver.py ${SERVER_PORT} > $LOGF 2>&1 &
		echo $! > $PIDF
	else
		echo "Finance portal already started!"
	fi
	if [ ! -z "${NO_DEMO}" ];then
	    echo "Skipping DEMO"
	else
            if [ $demo_status -eq 0 ];then
    	    	echo "Starting finance demo"
    		unset FINANCE_DB
                nohup ${SRC}/runserver.py ${DEMO_PORT} > $DEMO_LOGF 2>&1 &
    	    	echo $! > $DEMO_PIDF
            else
	    	echo "Finance demo already started!"
	    fi
	fi
	;;
stop)
    check_status
	if [ $status -eq 0 ];then
	    echo "Finance portal already stopped"
	else
		kill -9 `cat $PIDF`
		rm -f $PIDF
	fi
	if [ $demo_status -eq 0 ];then
	    echo "Finance demo already stopped"
	else
		kill -9 `cat $DEMO_PIDF`
		rm -f $DEMO_PIDF
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
