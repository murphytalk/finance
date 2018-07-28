#!/usr/bin/env bash
FINANCE_DB="$HOME/finance.db"
BACKUP_DIR="$HOME/Backup2Gdrive/finance"

if [[ -z "$FINANCE_DB" || ! -f $FINANCE_DB ]];then
	echo Cannot find finance.db !
	exit 1
fi

if [[ ! -d $BACKUP_DIR ]];then
    echo No backup dir $BACKUP_DIR
    exit 1
fi


find $BACKUP_DIR -name "*.bz2" -atime +7 -exec rm -f {} \;

temp=$BACKUP_DIR/finance.db.bz2
bzip2 -c $FINANCE_DB > $temp

if [ $? -eq 0 ];then
	rclone copy $temp gdrive:/finance
	f=$BACKUP_DIR/finance.db.`date +%Y%m%d`.bz2
	[ -f $f ] && rm -f $f
	mv $temp $f
else
	echo bzip2 failed
fi

