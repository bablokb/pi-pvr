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
  if ! $PVR_BIN_PATH/pvrctl.py -q -N "$delta_rec_on_boot"; then
    # no recording within delta, so give the system some time
    # to update the EPG and shutdown again
    logger -t pvr_on_boot \
         "no recording within $delta_rec_on_boot, shutting down in $shutdown_delay_on_boot minutes"
    shutdown -h +"$shutdown_delay_on_boot"
  else
    logger -t pvr_on_boot "next recording within $delta_rec_on_boot, do nothing"
  fi
else
  logger -t pvr_on_boot "normal startup, do nothing"
fi
