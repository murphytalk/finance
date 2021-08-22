#!/usr/bin/env bash
FINANCE_DB="/mnt/nas/vault/docker/finance/finance.db"
BACKUP_DIR="/mnt/nas/backup/DATA/finance"

if [[ -z "$FINANCE_DB" || ! -f $FINANCE_DB ]];then
	echo Cannot find db:  $FINANCE_DB !
	exit 1
fi

if [[ ! -d $BACKUP_DIR ]];then
    echo No backup dir $BACKUP_DIR
    exit 1
fi


bzip2 -c $FINANCE_DB > $BACKUP_DIR/finance.db.`date +%Y%m%d`.bz2
if [ $? -eq 0 ];then
	rclone sync $BACKUP_DIR tank:/backup/finance
    find $BACKUP_DIR -name "*.bz2" -atime +7 -exec rm -f {} \;
else
	echo bzip2 failed
fi

