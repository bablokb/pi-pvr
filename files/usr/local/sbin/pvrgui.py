#!/usr/bin/python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
# Simple GUI for PVR - supports shutdown and start of kodi.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-pvr
#
# --------------------------------------------------------------------------

import sys, os, datetime, threading, signal, subprocess, json
import fbgui

from pvrcec import CECController as CECController

# --- global constants   -----------------------------------------------------

BG_COLOR = fbgui.Color.BLACK

FONT_SMALL  = 12
FONT_MEDIUM = 30
FONT_LARGE  = 48

WIDTH  = 1500
HEIGHT = 844

# ----------------------------------------------------------------------------

class PvrGui(fbgui.App):
  """ subclass of App for this application """

  # -------------------------------------------------------------------------

  def __init__(self,settings=fbgui.Settings()):
    """ constructor """

    super(PvrGui,self).__init__(settings=settings)
    self._stop_event = threading.Event()

    panel = self._get_widgets()
    panel.pack()
    self.set_widget(panel)

    self._cec = CECController(self)

  # -------------------------------------------------------------------------

  def _get_widgets(self):
    """ create widget-tree """
    
    main = fbgui.VBox("main",
                      settings=fbgui.Settings({
                        'margins': 20,
                        'padding': 10
                        }),
                      toplevel=True)
    # add date-box
    self._add_date_box(main)

    # add info-box
    # since we set weight only here, the infobx will take all available space
    self._info_box = fbgui.List("info_box",None,
                                 settings=fbgui.Settings({
                                  'bg_color': fbgui.Color.SILVER,
                                  'font_name': "FreeMonoBold.ttf",
                                  'radius': 0.1,
                                  'margins': 20,
                                  'width': 1.0,
                                  'weight': 1
                                  }),parent=main)
    # add button-box
    self._add_button_box(main)

    return main

  # -------------------------------------------------------------------------

  def _add_date_box(self,main):
    """ add date-box """

    panel = fbgui.Panel("date_box",
                         settings=fbgui.Settings({
                          'bg_color': fbgui.Color.SILVER,
                          'radius': 0.9,
                          'margins': 20,
                          'width': 1.0,
                          'height': 0.093
                          }),parent=main)
    self._msg = fbgui.Label("msg_label","initializing...",
                            settings=fbgui.Settings({
                              'align': fbgui.LEFT
                           }),parent=panel)
    self._date = fbgui.Label("date_label","",
                            settings=fbgui.Settings({
                              'align': fbgui.RIGHT
                           }),parent=panel)

  # -------------------------------------------------------------------------

  def _add_button_box(self,main):
    """ add button-box """
    box = fbgui.HBox("button_box",
                     settings=fbgui.Settings({
                       'width': 1.0,
                       'uniform': True,
                       'height': 0.093,
                       'padding': 12,
                       }),parent=main)
    
    fbgui.Button("btn_red",None,"Off",
                 settings=fbgui.Settings({
                   'weight': 1,
                   'bg_color': fbgui.Color.RED
                   }),parent=box)
    
    fbgui.Button("btn_green",None,"Standby",
                 settings=fbgui.Settings({
                   'weight': 1,
                   'bg_color': fbgui.Color.GREEN
                   }),parent=box)
    
    fbgui.Button("btn_yellow",None,"Kodi",
                 settings=fbgui.Settings({
                   'weight': 1,
                   'bg_color': fbgui.Color.YELLOW
                   }),parent=box)
    
    fbgui.Button("btn_blue",None,"Off-mode",
                 settings=fbgui.Settings({
                   'weight': 1,
                   'bg_color': fbgui.Color.BLUE
                   }),parent=box)

  # -------------------------------------------------------------------------

  def _create_list_entry(self,entry,nr):
    """ create a HBox for the info-box """

    fbgui.App.logger.msg("DEBUG","creating entry for %r" % (entry,))
    text = "%s %s %s %s %s" % (entry['status'],
                         entry['channel'],
                         entry['title'],
                         entry['date'],
                         entry['time'])
    prefix = "entry_%d" % nr
    hbox = fbgui.HBox(prefix+"_hbox",
                      settings=fbgui.Settings({
                        'bg_color': fbgui.Color.SILVER,
                        'padding': 10,
                        'width': 1.0
                        }))
    settings = fbgui.Settings({
      'bg_color': fbgui.Color.SILVER,
      'align': (fbgui.LEFT,fbgui.BOTTOM),
      'font_size': FONT_MEDIUM,
      })
    fbgui.Label(prefix+"_status",entry['status'],
                settings=settings,parent=hbox)
    settings.width=0.15
    fbgui.Label(prefix+"_channel",entry['channel'],
                settings=settings,parent=hbox)
    fbgui.Label(prefix+"_date",entry['date'],
                settings=settings,parent=hbox)
    fbgui.Label(prefix+"_time",entry['time'],
                settings=settings,parent=hbox)
    settings.width=0.5
    fbgui.Label(prefix+"_title",entry['title'],
                settings=settings,parent=hbox)
    return hbox

  # -------------------------------------------------------------------------

  def _update_datetime(self):
    """ update datetime """

    now = datetime.datetime.now()
    self._date.set_text(now.strftime("%a %d.%m.%y %H:%M"),refresh=True)

  # -----------------------------------------------------------------------

  def update_msg(self):
    """ update message """

    try:
      status = subprocess.check_output(['pvrctl.py','-s']).decode('utf-8')
      if status.startswith("normal"):
        msg = "no automatic halt"
      else:
        msg = "turned off after next recording"
    except:
      msg = "does not turn off automatically"
    self._msg.set_text(msg,refresh=True)

  # -----------------------------------------------------------------------

  def _update_info(self):
    """ update info-box """

    # query information
    try:
      info = subprocess.check_output(
        ['pvrctl.py','-u','-f','json']).decode('utf-8')
      entries = json.loads(info)['entries']
    except:
      entries = [" "]

    # now clear and update info-box
    self._info_box.clear(refresh=False)
    index = 0
    for entry in entries[:-1]:
      self._info_box.add_items([self._create_list_entry(entry,index)],
                               refresh=False)
      index += 1
    self._info_box.post_layout()

  # -----------------------------------------------------------------------

  def _update(self):
    """ update on-screen information """

    delay = 0.01
    while True:
      if self._stop_event.wait(delay):
        # external break request
        break

      # update datetime
      self._update_datetime()

      # update message-area
      self.update_msg()

      # update info-area
      self._update_info()

      # check for external break every 15 seconds, but don't miss time-change
      delay = min(60 - datetime.datetime.now().second,15)

  # -----------------------------------------------------------------------

  def on_start(self):
    """ override base-class on_start-method """

    # setup async-thread
    update_thread = threading.Thread(target=myapp._update)
    update_thread.start()

  # -----------------------------------------------------------------------

  def on_quit(self,rc=0):
    """ override base-class quit-method """

    rc = super(PvrGui,self).on_quit(rc=rc)
    self._stop_event.set()
    sys.exit(rc)

  # ----------------------------------------------------------------------------

if __name__ == '__main__':

  config               = fbgui.Settings()
  config.msg_level     = "WARN"
  config.msg_syslog    = True
  config.bg_color      = BG_COLOR
  config.font_name     = "FreeSans"
  config.font_size     = FONT_LARGE
  config.width         = WIDTH
  config.height        = HEIGHT
  config.title         = "Status PVR"
  config.mouse_dev     = None
  config.mouse_visible = False

  myapp = PvrGui(config)
  myapp.run()
