#!/bin/bash
# --------------------------------------------------------------------------
# Helper script executed on after a recording from tvheadend
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-pvr
#
# --------------------------------------------------------------------------

# source configuration
. /etc/pvrctl.rc

# shutdown the system after a recording unless
#   - the system was manually started
#   - the next recording is within delta_rec

if [ $(cat /var/run/wake-on-rtc.status) = "normal" ]; then
  logger -t pvr_after_recording "normal startup, do nothing"
  return
fi

if ! pvrctl.py -q -N "$delta_rec_after_recording"; then
  # no recording within delta_rec, so shutdown
  logger -t pvr_after_recording \
         "next recording not within $delta_rec_after_recording, shutting down"
  sudo shutdown -h +"$shutdown_delay_after_recording"
else
  logger -t pvr_after_recording \
         "next recording within $delta_rec_after_recording, do nothing"
fi
