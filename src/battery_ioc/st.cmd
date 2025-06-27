#!/bin/sh
sleep 5h
echo "Starting IOC with softIoc..."
exec caRepeater & softIoc -D /epics/epics-base/dbd/softIoc.dbd -d /ioc/records.db -S