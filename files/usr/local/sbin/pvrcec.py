#!/usr/bin/python
# --------------------------------------------------------------------------
# Simple GUI for PVR - supports shutdown and start of kodi.
#
# This class implements the CEC-controller.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-pvr
#
# --------------------------------------------------------------------------

import os, subprocess, time
import pygame

try:
  import cec
  have_cec_import = True
except ImportError:
  print("[WARNING] could not import cec")
  have_cec_import = False

class CECController(object):
  """ class CECController - a CEC controller """

  KEY_BOUNCE_TIME = 5

  def __init__(self,app):
    """ initialization """

    self._app      = app
    self._have_cec = False
    self._last_key = time.monotonic()          # last time key was pressed
    if have_cec_import:
      self._init_cec()
      pygame.fastevent.init()
    else:
      self._app.logger.msg("WARN","import cec failed")

  # --- initialize CEC   ------------------------------------------------------

  def _init_cec(self):
    """ initialize CEC if available """

    self._log_level = cec.CEC_LOG_WARNING
    self._cecconfig = cec.libcec_configuration()
    self._cecconfig.strDeviceName   = "pvr"
    self._cecconfig.bActivateSource = 0
    self._cecconfig.deviceTypes.Add(cec.CEC_DEVICE_TYPE_RECORDING_DEVICE)
    self._cecconfig.clientVersion = cec.LIBCEC_VERSION_CURRENT

    self._cecconfig.SetLogCallback(self._process_logmessage)
    self._cecconfig.SetKeyPressCallback(self._process_key)
    self._cecconfig.SetCommandCallback(self._process_command)

    self._controller = cec.ICECAdapter.Create(self._cecconfig)
    self._app.logger.msg("DEBUG","libCEC version " +
          self._controller.VersionToString(self._cecconfig.serverVersion) +
          " loaded: " + self._controller.GetLibInfo())

    # search for adapters
    self._com_port = self._get_com_port()

    if self._com_port == None:
      self._app.logger.msg("ERROR","no port")
      self._have_cec = False
      return
    
    if not self._controller.Open(self._com_port):
      self._app.logger.msg("ERROR","could not open cec-adapter")
      self._have_cec = False
    else:
      #sems to be necessary at least with my DENON
      self._controller.GetActiveDevices()


  # --- process key presses   ------------------------------------------------

  def _post_quit(self,rc):
    """ post quit event to application """

    event = pygame.fastevent.Event(pygame.QUIT,rc=rc)
    pygame.fastevent.post(event)

  # --- process key presses   ------------------------------------------------
  
  def _process_key(self, key, duration):
    """ process keys """

    # if the remote sends keys, we could map the keys to commands here
    self._app.logger.msg("DEBUG","key: " + str(key))

    now = time.monotonic()
    if now - self._last_key < CECController.KEY_BOUNCE_TIME:
      self._app.logger.msg("DEBUG","ignoring key-press (bounce)")
      return 0
    else:
      self._last_key = now

    if key == cec.CEC_USER_CONTROL_CODE_F1_BLUE:
      self._app.logger.msg("DEBUG","key blue pressed")
      subprocess.call(['/usr/local/bin/pvrctl.py','-H'])
      self._app.update_msg()
    elif key == cec.CEC_USER_CONTROL_CODE_F2_RED:
      self._app.logger.msg("DEBUG","key red pressed")
      self._controller.StandbyDevices(cec.CECDEVICE_BROADCAST)
      self._post_quit(3)
    elif key == cec.CEC_USER_CONTROL_CODE_F3_GREEN:
      self._app.logger.msg("DEBUG","key green pressed")
      self._controller.StandbyDevices(cec.CECDEVICE_BROADCAST)
    elif key == cec.CEC_USER_CONTROL_CODE_F4_YELLOW:
      self._app.logger.msg("DEBUG","key yellow pressed")
      self._post_quit(0)

    return 0

  # --- process commands   ---------------------------------------------------
  
  def _process_command(self, cmd):
    """ process commands """

    # if the remote sends (correct) commands, we could take actions here
    # e.g. turn on the radio
    self._app.logger.msg("DEBUG","cec command: " + cmd)
    return 0

  # --- process log-messages   ------------------------------------------------
  
  def _process_logmessage(self, level, time, message):
    """ process log messages (just send them to debug-output) """
    if level > self._log_level:
      return 0

    if level == cec.CEC_LOG_ERROR:
      ceclevel = "CEC-ERROR: "
      levelstr = "ERROR"
    elif level == cec.CEC_LOG_WARNING:
      ceclevel = "CEC-WARNING: "
      levelstr = "WARN"
    elif level == cec.CEC_LOG_NOTICE:
      ceclevel = "CEC-NOTICE: "
      levelstr = "INFO"
    elif level == cec.CEC_LOG_TRAFFIC:
      ceclevel = "CEC-TRAFFIC: "
      levelstr = "TRACE"
    elif level == cec.CEC_LOG_DEBUG:
      ceclevel = "CEC-DEBUG: "
      levelstr = "DEBUG"

    self._app.logger.msg(levelstr,ceclevel + "[" + str(time) + "]     " + message)
    return 0

  # --- return com port path of adapter   -------------------------------------

  def _get_com_port(self):
    """ query (first) available adapter """

    for adapter in self._controller.DetectAdapters():
      self._app.logger.msg("DEBUG","CEC Adapter:")
      self._app.logger.msg("DEBUG","Port:     " + adapter.strComName)
      self._app.logger.msg("DEBUG","vendor:   " + hex(adapter.iVendorId))
      self._app.logger.msg("DEBUG","Produkt:  " + hex(adapter.iProductId))
      return adapter.strComName

    self._app.logger.msg("DEBUG","no cec adapter found")
    return None

  # --- return cec-availability   ---------------------------------------------

  def have_cec(self):
    """ return cec-availability """

    return self._have_cec

  # --- set as active source   ------------------------------------------------

  def set_active_source(self):
    """ set as active source """
    if self._have_cec:
      self._controller.SetActiveSource()
