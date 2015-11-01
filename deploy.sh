#!/usr/bin/bash
d=`dirname $0`


cmd=x"$1"
if [[ $cmd == "xc" ]];then
	echo "Only copy WAR file ..."
else
	cd $d
	mvn vaadin:compile-theme
	mvn package
	cd -
fi
pom=$d/pom.xml
version=`grep SNAPSHOT $pom|sed 's/.*>\(.*\)<\/version>.*/\1/g'`
scp -P $VPS_PORT $d/target/finance-${version}.war $FINANCE_REMOTE_DEPLOYMENT_DIR/webapps/ROOT.war

