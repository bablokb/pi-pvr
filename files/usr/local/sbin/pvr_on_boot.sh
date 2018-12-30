#!/bin/bash
# --------------------------------------------------------------------------
# Helper script executed on boot from pi-wake-on-rtc service
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-pvr
#
# --------------------------------------------------------------------------

delta_rec="01:00"    # one hour
delta_shutdown="30"  # 30 minutes

# we only do something special on an rtc alarm

if [ "$1" = "alarm" ]; then
  if ! pvrctl.py -q -N "$delta"; then
    # no recording within delta, so give the system some time
    # to update the EPG and shutdown again
    shutdown -p +"$delta_shutdown"
fi
