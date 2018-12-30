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

# --- system imports   -----------------------------------------------------

from argparse import ArgumentParser
from operator import itemgetter
import sys, os, datetime, pprint
import requests
import configparser

# --- private imports   -----------------------------------------------------

from pvrctl_msg      import Msg as Msg

# --- helper-class for options   --------------------------------------------

class Options(object):
  pass

# --- query upcoming events   -----------------------------------------------

def api_upcoming():
  """ query upcoming events """

  url = "http://%s:%s@%s:9981/%s" % (
                                    options.config['user'],
                                    options.config['password'],
                                    options.config['hostname'],
                                    TVHEADEND_UPCOMING_API)
  try:
    req = requests.get(url)
    return sorted(req.json()['entries'], key=itemgetter('start_real'))
  except:
    return []

# --- print upcoming recordings   -------------------------------------------

def print_upcoming(options,all=True):
  """ output upcoming recordings """

  next_recordings = api_upcoming()

  for rec in next_recordings:
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

  next_recordings = api_upcoming()
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

  next_recordings = api_upcoming()
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

# --- process boot logic   --------------------------------------------------

def process_boot_logic(options):
  """ process boot logic """
  pass

# --- process post recording logic   ----------------------------------------

def process_post_rec_logic(options):
  """ process post recording logic """
  pass

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
  parser.add_argument('-b', '--boot', action='store_true',
    dest='do_boot',
    help='execute boot-hook logic')
  parser.add_argument('-p', '--post-rec', action='store_true',
    dest='do_post',
    help='execute post-recording logic')

  parser.add_argument('-q', '--quiet', default=False, action='store_true',
    dest='quiet',
    help='do not print anything')
  parser.add_argument('-l', '--level', metavar='Log-Level',
    dest='level', default='INFO',
    help='print messages at least of given level')
  parser.add_argument('-h', '--help', action='help',
    help='print this help')

  parser.add_argument('arguments', nargs='*', metavar='program-arguments',
    help='additional program arguments')
  return parser

# --- create configuration object   -----------------------------------------

def get_config(parser):
  return {
    "MSG_LEVEL":           parser.get('CONFIG',"MSG_LEVEL"),
    "NO_SHUTDOWN_BEFORE":  parser.getint('CONFIG',"NO_SHUTDOWN_BEFORE"),

    "hostname":            parser.get('SERVER',"hostname"),
    "user":                parser.get('SERVER',"user"),
    "password"  :          parser.get('SERVER',"password")
    }

# --- main proram   ---------------------------------------------------------

if __name__ == '__main__':

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

  # add global objects
  options.config = config

  if options.do_next:
    print_next_rec_time(options)
  elif options.do_upcoming:
    print_upcoming(options)
  elif options.span:
   check_next_rec_time(options)
  elif options.do_boot:
    process_boot_logic(options)
  elif options.do_post:
    process_post_rec_logic(options)
  sys.exit(0)

