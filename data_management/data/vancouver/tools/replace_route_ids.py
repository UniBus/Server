#!/usr/bin/python
#
#  replace_route_ids.py
#  
#
#  Created by Zhenwang Yao on 03/11/08.
#  Copyright (c) 2008 Music Motion. All rights reserved.
#

## This module import replace stop_id with stop_code in
#    - routes.txt, and
#    - trips.txt
#

import csv
import sys
import string
import os

def update_routes(newfilename, filename):
	idsToNames = {}
	namesToIds = {}
	try:
		print "   [*] Opening file %s reading" % filename
		cvsfile = open(filename)
		headerreader = csv.reader(cvsfile,skipinitialspace=True)
		fieldnames = headerreader.next()
		reader = csv.DictReader(cvsfile, fieldnames, restkey='unknown', restval='',skipinitialspace=True)
		#print fieldnames

		print "   [*] Opening file %s for writing" % newfilename
		output = open(newfilename, "w")
		output.write("route_id,route_short_name,route_long_name,route_type\n")

		print "   [*] Adding records into route dictionary "
		addLines = 0
		currentLine = 1
		for rowvalues in reader:
			currentLine = currentLine + 1
			route_id = rowvalues['route_id'] #.strip(), will slow down a lot
			route_name = rowvalues['route_short_name'] #.replace('&', '&amp;')
			
			#print route_name
			if route_name.isdigit():
				route_name = "%03d" % string.atoi(route_name, 10)			
			idsToNames[route_id] = route_name

			if route_name in namesToIds:
				continue
			namesToIds[route_name] = route_id

			route_short_name = rowvalues['route_short_name']
			route_long_name = rowvalues['route_long_name'].title()

			#print route_name
			output.write("%s, %s, %s, %s\n" % (route_name, route_short_name, route_long_name, rowvalues['route_type'] ))
			#print route_name, rowvalues['route_short_name'], rowvalues['route_long_name'], rowvalues['route_type']

			addLines = addLines + 1
		
		#check
		print "   [*] Number of lines read from ", filename, ": %d" %currentLine	
		print "   [*] Number of lines written to ", newfilename, ": %d" %addLines	
		print "   [*] Done \n"

		output.close()
		cvsfile.close()
		return idsToNames

	except Exception as ex:
		print "Exception with message:  %s!!" % str(ex)
		sys.exit(1)
	

def update_trips(newfilename, filename, routedict):
	try:
		#insert record
		print "   [*] Opening file %s for reading " % filename
		cvsfile = open(filename)
		headerreader = csv.reader(cvsfile,skipinitialspace=True)
		fieldnames = headerreader.next()
		reader = csv.DictReader(cvsfile, fieldnames, restkey='unknown', restval='',skipinitialspace=True)
		#print fieldnames

		print "   [*] Opening file %s for writing" % newfilename
		output = open(newfilename, "w")
		output.write("block_id,route_id,direction_id,trip_headsign,shape_id,service_id,trip_id\n")
		#print "block_id,route_id,direction_id,trip_headsign,shape_id,service_id,trip_id"
		
		print "   [*] Reading records "
		addLines = 0
		currentLine = 1
		for rowvalues in reader:
			currentLine = currentLine + 1
			route_id = rowvalues['route_id'] #.strip(), will slow down a lot
			trip_headsign = rowvalues['trip_headsign'].title()
			#print route_id, trip_headsign

			output.write("%s, %s, %s, %s, %s, %s, %s\n"%(rowvalues['block_id'],routedict[route_id],rowvalues['direction_id'], trip_headsign, rowvalues['shape_id'],rowvalues['service_id'],rowvalues['trip_id']))

			addLines = addLines + 1
		
		#check
		print "   [*] Number of lines read from ", filename, ": %d" %currentLine	
		print "   [*] Number of lines written to ", newfilename, ": %d" %addLines	
		print "   [*] Done \n"

		#close down
		cvsfile.close()
		output.close()

	except Exception as ex:
		print "Exception with message:  %s!!" % str(ex)
		sys.exit(1)



if __name__ == '__main__':
	routedict = update_routes('routes.txt', 'routes_origin.txt')
	update_trips('trips_new.txt', 'trips_origin.txt', routedict)


