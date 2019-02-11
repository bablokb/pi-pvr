PVR based on Raspbian Stretch and TVHeadend
===========================================

This project contains a number of scripts and configuration files for the
management of automatic boot and shutdown of a Pi running tvheadend.

The project is a supplementary project to my project
[pi-wake-on-rtc](https://www.github.com/bablokb/pi-wake-on-rtc "Wake-On-RTC").

The project provides the following scripts:

  - `pvrctl.py`: general utility-script (interfaces tvheadend)
  - `pvr_on_boot.sh`: hook-script to execute after boot
  - `pvr_on_halt.sh`: hook-script to execute on halt
  - `pvr_after_recording.sh`: script to execute after every recording
