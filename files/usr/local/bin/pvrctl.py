#!/usr/bin/python3
# -*- coding: utf-8 -*-
# --------------------------------------------------------------------------
# Control-script for tvheadend-based pvr
#
# Main program.
#
# Author: Bernhard Bablok
# License: GPL3
#
# Website: https://github.com/bablokb/pi-pvr
#
# --------------------------------------------------------------------------

TVHEADEND_UPCOMING_API="api/dvr/entry/grid_upcoming"
STATUS_FILE="/var/run/wake-on-rtc.status"

# --- system imports   -----------------------------------------------------

from argparse import ArgumentParser
from operator import itemgetter
import sys, os, datetime, pprint, locale
import requests
import configparser

# --- private imports   -----------------------------------------------------

from pvrctl_msg      import Msg as Msg

# --- helper-class for options   --------------------------------------------

class Options(object):
  pass

# --- query upcoming events   -----------------------------------------------

def api_upcoming(options):
  """ query upcoming events """

  url = "http://%s:%s@%s:9981/%s" % (
                                    options.config['user'],
                                    options.config['password'],
                                    options.config['hostname'],
                                    TVHEADEND_UPCOMING_API)
  try:
    req = requests.get(url)
    recordings = sorted(req.json()['entries'], key=itemgetter('start_real'))
    if options.ignore_running:
      return [r for r in recordings if r["status"] != "Running"]
    else:
      return recordings
  except:
    return []

# --- set status   ----------------------------------------------------------

def set_status(options):
  """ set boot/auto-halt status """

  if options.do_halt_mode == "toggle":
    old_mode = get_status(options)
    if old_mode == "normal":
      new_mode = "alarm"
    elif old_mode == "alarm":
      new_mode = "normal"
    else:
      new_mode = "alarm"
  else:
    new_mode = options.do_halt_mode

  with open(STATUS_FILE,"w") as sfile:
    status = sfile.write(new_mode)

# --- get status   ----------------------------------------------------------

def get_status(options):
  """ get boot/auto-halt status """

  if os.path.exists(STATUS_FILE):
    with open(STATUS_FILE,"r") as sfile:
      status = sfile.readline()
  else:
    status = 'normal'
  return status

# --- print status   --------------------------------------------------------

def print_status(options):
  """ print boot/auto-halt status """

  status = get_status(options)
  if status == "normal":
    status = "normal boot, no automatic halt after next recording"
  elif status == "alarm":
    status = "automatic boot, automatic halt after next recording"
  else:
    status = "unknown boot-status"
  print(status)

# --- print upcoming recordings   -------------------------------------------

def print_upcoming(options,all=True):
  """ output upcoming recordings """

  next_recordings = api_upcoming(options)

  for rec in next_recordings:
    if options.format == 'raw':
      pprint.pprint(rec)
    elif options.format == 'json':
      start = datetime.datetime.fromtimestamp(rec['start'])
      end   = datetime.datetime.fromtimestamp(rec['stop'])
      print("""{'status': '%s',
              'channel': '%s',
              'title': '%s',
              'date': '%s',
              'time': '%s-%s'}""" % (
        rec['status'][0],
        rec['channelname'],
        rec['disp_title'],
        start.strftime("%x"),
        start.strftime("%H:%M"),
        end.strftime("%H:%M")))
    elif options.format == 'compact':
      start = datetime.datetime.fromtimestamp(rec['start'])
      end   = datetime.datetime.fromtimestamp(rec['stop'])
      print("%s %s %s %s-%s" % (
        rec['status'][0],
        rec['channelname'],
        rec['disp_title'],
        start.strftime("%a %d.%m.%y %H:%M"),
        end.strftime("%H:%M")))
    else:
      start = datetime.datetime.fromtimestamp(rec['start_real'])
      end   = datetime.datetime.fromtimestamp(rec['stop_real'])
      print("""
channel:  %s
title:    %s
status:   %s
start:    %s
end:      %s\n""" % (rec['channelname'],
                     rec['disp_title'],
                     rec['status'],
                     start.strftime("%c"),
                     end.strftime("%c")))
    if not all:
      return    # after printing first entry

# --- output next recording time   ------------------------------------------

def print_next_rec_time(options,out=True):
  """ output next recording time """

  next_recordings = api_upcoming(options)
  if len(next_recordings):
    start = datetime.datetime.fromtimestamp(next_recordings[0]['start_real'])
    print(start.strftime("%Y-%m-%d %H:%M:%S"))
  else:
    print("0")

# --- parse span-value and return timedelta object   -----------------------

def parse_span(value):
  """ parse span-value and return timedelta object """

  # parse span-value  [days] HH:MM
  delta_span = value.split(" ")
  if len(delta_span) > 1:
    delta_d    = int(delta_span[0])
    delta_span = delta_span[1]
  else:
    delta_d    = 0
    delta_span = delta_span[0]

  delta_span = delta_span.split(":")
  delta_h    = int(delta_span[0])
  if len(delta_span) > 1:
    delta_m = int(delta_span[1])
  else:
    delta_m = 0

  return datetime.timedelta(days=delta_d,hours=delta_h,minutes=delta_m)

# --- check next recording time   ------------------------------------------

def check_next_rec_time(options,out=True):
  """ output next recording time """

  Msg.msg("INFO","checking next recording within time-span of %s" % options.span)
  delta = parse_span(options.span)
  Msg.msg("DEBUG","delta: %s" % delta)

  next_recordings = api_upcoming(options)
  have_rec = False
  if len(next_recordings):
    delta = parse_span(options.span)
    start = datetime.datetime.fromtimestamp(next_recordings[0]['start_real'])
    if start - datetime.datetime.now() <= delta:
      have_rec = True

  if have_rec:
    Msg.msg("INFO","next recording within time-span of %s" % options.span)
    sys.exit(0)
  else:
    Msg.msg("INFO","next recording not within time-span of %s" % options.span)
    sys.exit(1)

# --- commandline parser  ---------------------------------------------------

def get_parser():
  parser = ArgumentParser(add_help=False,
    description='manage boot and shutdown of pvr')
  
  parser.add_argument('-u', '--upcoming-recordings', action='store_true',
    dest='do_upcoming',
    help='print start-time of next recording')
  parser.add_argument('-n', '--next-rec-time', action='store_true',
    dest='do_next',
    help='print start-time of next recording')
  parser.add_argument('-N', '--next-rec-within', metavar='time-span',
    dest='span', default=None,
    help='check if a recording is scheduled within time-span')
  parser.add_argument('-i', '--ignore-running', action='store_true',
    dest='ignore_running',
    help='ignore running recordings (use with -u, -n or -N)')
  parser.add_argument('-f', '--format', metavar='format',
    dest='format', default='human',
    choices=['human','compact','json','raw'],
    help='format: one of human, compact, json, raw')

  parser.add_argument('-s', '--status', action='store_true',
    dest='do_status',
    help='show boot/auto-halt status')
  parser.add_argument('-H', '--halt', metavar='halt-mode', nargs="?",
    dest='do_halt_mode', default=None, const='toggle',
    choices=['normal','auto','toggle'],
    help='halt-mode: normal (no automatic halt) or auto (halt after next recording)')

  parser.add_argument('-q', '--quiet', default=False, action='store_true',
    dest='quiet',
    help='do not print anything (sets log-level to NONE)')
  parser.add_argument('-l', '--level', metavar='Log-Level',
    dest='level', default='INFO',
    choices=['NONE','ERROR','WARN','INFO','DEBUG','TRACE'],
    help='log level: one of NONE, ERROR, WARN, INFO, DEBUG, TRACE')
  parser.add_argument('-h', '--help', action='help',
    help='print this help')

  parser.add_argument('arguments', nargs='*', metavar='program-arguments',
    help='additional program arguments')
  return parser

# --- create configuration object   -----------------------------------------

def get_config(parser):
  return {
    "MSG_LEVEL":           parser.get('CONFIG',"MSG_LEVEL"),

    "hostname":            parser.get('SERVER',"hostname"),
    "user":                parser.get('SERVER',"user"),
    "password"  :          parser.get('SERVER',"password")
    }

# --- main proram   ---------------------------------------------------------

if __name__ == '__main__':

  # set local to default from environment
  locale.setlocale(locale.LC_ALL, '')

  config_parser = configparser.RawConfigParser()
  config_parser.read('/etc/pvrctl.conf')
  try:
    config = get_config(config_parser)
  except Exception as e:
    print("configuration error!")
    print("ERROR: %s" % e.message)
    sys.exit(3)

  opt_parser = get_parser()
  options = opt_parser.parse_args(namespace=Options)

  # configure Msg-class
  if options.level:
    Msg.level = options.level
  else:
    Msg.level = config["MSG_LEVEL"]
  if options.quiet:
    Msg.level = 'NONE'

  # add global objects
  options.config = config

  if options.do_halt_mode:
    set_status(options)
  elif options.do_status:
    print_status(options)
  elif options.do_next:
    print_next_rec_time(options)
  elif options.do_upcoming:
    print_upcoming(options)
  elif options.span:
   check_next_rec_time(options)
  sys.exit(0)

