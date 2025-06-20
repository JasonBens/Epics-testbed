#!/bin/sh
echo "Starting IOC with softIoc..."
exec softIoc -D /epics/epics-base/dbd/softIoc.dbd -d /ioc/records.db -S