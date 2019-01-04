#!/bin/bash
# --------------------------------------------------------------------------
# Helper script executed on halt from pi-wake-on-rtc service
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-pvr
#
# --------------------------------------------------------------------------

no_rec_limit="36:00"    # check for recordings within this time
idle_boot_at="06:00"    # next boot, if no recording is scheduled

if pvrctl.py -i -q -N "$no_rec_limit"; then
  pvrctl.py -i -n
else
  date -d "tomorrow $idle_boot_at" +"%Y-%m-%d %H:%M:%S"
fi
