#!/bin/sh
cd /ioc

echo "Starting softIOC..."
exec /epics/epics-base/bin/linux-x86_64/softIoc -S -D /epics/epics-base/dbd/softIoc.dbd -d records.db