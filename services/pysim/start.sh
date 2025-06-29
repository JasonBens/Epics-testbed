#!/bin/sh
cd /ioc

echo "Starting softIOC..."
/epics/epics-base/bin/linux-x86_64/softIoc -S -D /epics/epics-base/dbd/softIoc.dbd -d records.db &
IOC_PID=$!

cd /usr/src/app/sim
echo "Starting python sim..."
python -u sim.py &
SIM_PID=$!

# Wait for all processes
wait $IOC_PID
wait $SIM_PID