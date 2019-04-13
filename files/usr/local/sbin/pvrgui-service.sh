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
  # start pvrgui.py and wait for it's termination
  logger -t "pvrgui" "starting pvrgui"
  /usr/local/sbin/pvrgui.py
  if [ $? -eq 3 ]; then
    # quit the service and shutdown in case pvrgui.py returns 3
    logger -t "pvrgui" "pvrgui ended with rc=3. Exiting ..."
    break
  fi
  logger -t "pvrgui" "starting kodi"
  /usr/bin/kodi
  logger -t "pvrgui" "kodi ended with rc=$?"
done

logger -t "pvrgui" "starting shutdown"
/sbin/shutdown now
