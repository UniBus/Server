#!/usr/bin/python
#
#  purify.py
#  
#
#  Created by Zhenwang Yao on 03/11/08.
#  Copyright (c) 2008 Music Motion. All rights reserved.
#

## This module remove unnecessary services, trips and stop_times, in order to create more compact data
#    - calendar.txt,
#    - calendar_dates.txt,
#    - trips.txt,
#    - stop_times.txt
#

#  replace_route_ids.py
#  replace_stop_ids.py
#  simplify_trips_times.py

from replace_route_ids import *
from replace_stop_ids import *
from simplify_trips_times import *
from sets import Set
import string
import os
import sys
import getopt

def usage():
	print 'Usage:'
	print '\t %s  [options] <start_date> <end_date>' % (os.path.basename(sys.argv[0]))
	print 'Options:'
	print '\t --help              This information'
	print '\t --disable-stop      Disable stop pre-processing'
	print '\t --disable-route     Disable routst pre-processing'
	print '\t --disable-calendar  Disable calendar pre-processing'
	print ''
	print '\t start_end/end_date in form of YYYYMMDD'
	print '\t    for example, 20091201'
	print ''

try:                                
	opts, args = getopt.getopt(sys.argv[1:], "hsrc", ["help", "disable-stop", "disable-route", "disable-calendar"])
except getopt.GetoptError:
	print "Parameter parsing error"
	usage()
	sys.exit(1)

start = "00000000"
end = "21111111"
disable_route = 0
disable_stop = 0
disable_calendar = 0

#print "args: ", args
#print "opts: ", opts
for opt, arg in opts:
	if opt in ("-h", "--help"):
		usage()
		sys.exit(1)
	if opt in ("-s", "--disable-stop"):
		disable_stop = 1
	if opt in ("-r", "--disable-route"):
		disable_route = 1
	if opt in ("-c", "--disable-calendar"):
		disable_calendar = 1

if len(args) >= 1:
	if not args[0].isdigit():
		usage()
		sys.exit(1)
	elif len(args[0]) != 8:
		usage()
		sys.exit(1)
	else:
		start = args[0]

if len(args) >= 2:
	if not args[1].isdigit():
		usage()
		sys.exit(1)
	elif len(args[1]) != 8:
		usage()
		sys.exit(1)
	else:
		end = args[1]

#print start, end
#print disable_stop, disable_route, disable_calendar
#sys.exit(1)
if disable_stop==0:
	stopdict = update_stops('stops.txt', 'stops_origin.txt')
	update_stop_times('stop_times_new.txt', 'stop_times_origin.txt', stopdict)

if disable_route==0:
	routedict = update_routes('routes.txt', 'routes_origin.txt')
	update_trips('trips_new.txt', 'trips_origin.txt', routedict)

if disable_calendar==0:
	services = simplify_calendar('calendar.txt', 'calendar_origin.txt', start, end )
	print services
	#services = simplify_calendar_dates('calendar_dates.txt', 'calendar_dates_origin.txt', services, start, end )

	#Note that calling this function actually change services
	#simplify_calendar_dates('calendar_dates.txt', 'calendar_dates_origin.txt', services, start, end )

	trips = simplify_trips('trips.txt', 'trips_new.txt', services)
	simplify_stop_times('stop_times.txt', 'stop_times_new.txt', trips)


