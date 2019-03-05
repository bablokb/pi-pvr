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

import sys, os, datetime, threading, signal
import fbgui

# --- global constants   -----------------------------------------------------

FG_COLOR = fbgui.Color.WHITE
BG_COLOR = fbgui.Color.BLACK

FONT_SMALL  = 12
FONT_MEDIUM = 24
FONT_LARGE  = 48

WIDTH  = 1920
HEIGHT = 1080

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
    self._info_box = fbgui.Panel("info_box",
                                 settings=fbgui.Settings({
                                   'bg_color': fbgui.Color.SILVER,           
                                   'margins': 20,
                                   'width': 1.0,
                                   'height': 800
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
                          'margins': 20,
                          'width': 1.0,
                          'height': 100
                          }),parent=main)
    self._msg = fbgui.Label("msg_label","Hallo Welt",
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
                       'height': 100,
                       'padding': 12,
                       }),parent=main)
    
    fbgui.Button("btn_red",None,"Off",
                 settings=fbgui.Settings({
                   'bg_color': fbgui.Color.RED,
                   'width': 461,
                   'height': 100
                   }),parent=box)
    
    fbgui.Button("btn_green",None,"Standby",
                 settings=fbgui.Settings({
                   'bg_color': fbgui.Color.GREEN,
                   'width': 461,
                   'height': 100
                   }),parent=box)
    
    fbgui.Button("btn_yellow",None,"Kodi",
                 settings=fbgui.Settings({
                   'bg_color': fbgui.Color.YELLOW,
                   'width': 461,
                   'height': 100
                   }),parent=box)
    
    fbgui.Button("btn_blue",None,"",
                 settings=fbgui.Settings({
                   'bg_color': fbgui.Color.BLUE,
                   'width': 461,
                   'height': 100
                   }),parent=box)

  # -------------------------------------------------------------------------

  def _cec_control(self):
    """ configure CEC """
    pass

  # -----------------------------------------------------------------------

  def on_start(self):
    """ override base-class on_start-method """

    now = datetime.datetime.now()
    self._date.set_text(now.strftime("%a %d.%m.%y %H:%M"))

    # setup async-thread
    #cec_thread = threading.Thread(target=myapp._cec_control)
    #cec_thread.start()

  # -----------------------------------------------------------------------

  def on_quit(self):
    """ override base-class quit-method """

    super(PvrGui,self).on_quit()
    self._stop_event.set()
    sys.exit(0)

  # ----------------------------------------------------------------------------

if __name__ == '__main__':

  config               = fbgui.Settings()
  config.msg_level     = "TRACE"
  config.bg_color      = BG_COLOR
  config.font_name     = "FreeSans"
  config.font_size     = FONT_LARGE
  config.width         = WIDTH
  config.height        = HEIGHT
  config.title         = "Status PVR"
  config.mouse_visible = False

  myapp = PvrGui(config)
  myapp.run()
