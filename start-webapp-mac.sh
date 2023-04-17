#!/bin/sh

logfile=$0.log

# start webapp/webhook-receiver (move to port 6001 to get away from Mac airplay issues)
export FLASK_APP=webapp
export FLASK_ENV=development
export PYTHONPATH=.
whereis python3
python3 -m flask run -p 6008 2>&1 |tee -a $logfile

