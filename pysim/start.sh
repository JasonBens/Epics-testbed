#!/bin/sh
cd /ioc
./st.cmd &
IOC_PID=$!
echo "Starting IOC with PID $IOC_PID"

cd /usr/src/app/sim
echo "Starting python sim..."
python sim.py

wait $IOC_PID
