#!/bin/bash

$HIVE_HOME/bin/schematool -info -dbType postgres > /tmp/schemacheck

SCHEMA=`cat /tmp/schemacheck | grep completed | wc -l`

# if [ 0 -eq $SCHEMA ]; then
$HIVE_HOME/bin/schematool -dbType postgres -initSchema
# fi

$HIVE_HOME/bin/hive --service hiveserver2
