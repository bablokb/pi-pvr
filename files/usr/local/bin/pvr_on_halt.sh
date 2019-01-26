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

# source configuration
. /etc/pvrctl.rc

if pvrctl.py -i -q -N "$delta_rec_on_halt"; then
  pvrctl.py -i -n
else
  date -d "tomorrow $idle_boot_at" +"%Y-%m-%d %H:%M:%S"
fi
