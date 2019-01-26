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

# source configuration
. /etc/pvrctl.rc

# we only do something special on an rtc alarm

if [ "$1" = "alarm" ]; then
  if ! pvrctl.py -q -N "$delta_rec_on_boot"; then
    # no recording within delta, so give the system some time
    # to update the EPG and shutdown again
    shutdown -h +"$shutdown_delay_on_boot"
fi
