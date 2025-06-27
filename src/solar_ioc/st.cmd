#!/epics/epics-base/bin/linux-x86_64/softIoc

cd /ioc

## Load the record database
dbLoadDatabase("/epics/epics-base/dbd/softIoc.dbd", 0, 0)
## softIocPVA_registerRecordDeviceDriver(pdbbase)

## Load your records
dbLoadRecords("records.db", "")

## Optional: Set environment or logging
# var epicsEnvShow

## Start the IOC
iocInit
