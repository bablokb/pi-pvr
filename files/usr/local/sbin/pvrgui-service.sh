#!/bin/bash
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
# Script for the systemd-service pvrgui.service
#
# This script alternatively starts the pvrgui.py application or kodi.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-pvr
#
# --------------------------------------------------------------------------

while true; do
  # start pvrgui.py in the background and wait for it's termination
  nohup /usr/local/sbin/pvrgui.py &
  wait $!
  if [ $? -eq 3 ]; then
    # quit the service in case pvrgui.py returns 3
    break
  fi
  /usr/bin/kodi &
  wait $!
done