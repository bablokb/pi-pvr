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

delta_rec="00:30"    # 30 minutes

# shutdown the system after a recording unless
#   - the system was manually started
#   - the next recording is within delta_rec

if [ $(cat /var/run/wake-on-rtc.status) = "normal" ]; then
  return
fi

if ! pvrctl.py -q -N "$delta_rec"; then
  # no recording within delta_rec, so shutdown
  sudo shutdown -h now
fi
