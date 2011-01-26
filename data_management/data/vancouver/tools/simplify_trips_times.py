#!/usr/bin/python
#
#  simplify_trips_times.py
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

import csv
import sys
import string
import os

def simplify_calendar(newfilename, filename, start, end):
	servicesToRemove = {}
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
		output.write("service_id,start_date,end_date,monday,tuesday,wednesday,thursday,friday,saturday,sunday\n")
		#print "block_id,route_id,direction_id,trip_headsign,shape_id,service_id,trip_id"
		
		print "   [*] Reading records "
		addLines = 0
		currentLine = 1
		for rowvalues in reader:
			currentLine = currentLine + 1
			service_id = rowvalues['service_id']
			start_date = rowvalues['start_date']
			end_date = rowvalues['end_date']
			if end_date < start:
				servicesToRemove[service_id] = 1
				continue
			elif start_date > end:
				servicesToRemove[service_id] = 1
				continue
			
			output.write("%s, %s, %s, %s, %s, %s, %s, %s, %s, %s\n"%(rowvalues['service_id'], \
										rowvalues['start_date'],\
										rowvalues['end_date'],\
										rowvalues['monday'],\
										rowvalues['tuesday'],\
										rowvalues['wednesday'],\
										rowvalues['thursday'],\
										rowvalues['friday'],\
										rowvalues['saturday'],\
										rowvalues['sunday']))

			addLines = addLines + 1
		
		#check
		print "   [*] Number of lines read from ", filename, ": %d" %currentLine	
		print "   [*] Number of lines written to ", newfilename, ": %d" %addLines	
		print "   [*] Done \n"

		#close down
		cvsfile.close()
		output.close()
		return servicesToRemove

	except Exception as ex:
		print "Exception with message:  %s!!" % str(ex)
		sys.exit(1)


def simplify_calendar_dates(newfilename, filename, services, start, end):
	servicesToRemove = services
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
		output.write("service_id,date,exception_type\n")
		#print "block_id,route_id,direction_id,trip_headsign,shape_id,service_id,trip_id"
		
		print "   [*] Reading records "
		addLines = 0
		currentLine = 1
		for rowvalues in reader:
			currentLine = currentLine + 1
			service_id = rowvalues['service_id']
			the_date = rowvalues['date']
			if the_date < start:
				servicesToRemove[service_id] = 1
				continue
			elif the_date > end:
				servicesToRemove[service_id] = 1
				continue
			
			output.write("%s, %s, %s\n" % ( rowvalues['service_id'], \
							rowvalues['date'],\
							rowvalues['exception_type']))

			addLines = addLines + 1
		
		#check
		print "   [*] Number of lines read from ", filename, ": %d" %currentLine	
		print "   [*] Number of lines written to ", newfilename, ": %d" %addLines	
		print "   [*] Done \n"

		#close down
		cvsfile.close()
		output.close()
		return servicesToRemove

	except Exception as ex:
		print "Exception with message:  %s!!" % str(ex)
		sys.exit(1)


def simplify_trips(newfilename, filename, services):
	tripsToRemove = {}
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
			
			if rowvalues['service_id'] in services:
				tripsToRemove[rowvalues['trip_id']] = 1
				continue

			route_id = rowvalues['route_id'] #.strip(), will slow down a lot
			output.write("%s, %s, %s, %s, %s, %s, %s\n"%(rowvalues['block_id'],\
									rowvalues['route_id'],\
									rowvalues['direction_id'],\
									rowvalues['trip_headsign'],\
									rowvalues['shape_id'],\
									rowvalues['service_id'],\
									rowvalues['trip_id']))

			addLines = addLines + 1
		
		#check
		print "   [*] Number of lines read from ", filename, ": %d" %currentLine	
		print "   [*] Number of lines written to ", newfilename, ": %d" %addLines	
		print "   [*] Done \n"

		#close down
		cvsfile.close()
		output.close()
		return tripsToRemove

	except Exception as ex:
		print "Exception with message:  %s!!" % str(ex)
		sys.exit(1)



def remove_unused_trips(newfilename, filename, trips):
	tripsToRemove = {}
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
			
			if not rowvalues['trip_id'] in trips:
				tripsToRemove[rowvalues['trip_id']] = 1
				continue

			route_id = rowvalues['route_id'] #.strip(), will slow down a lot
			output.write("%s, %s, %s, %s, %s, %s, %s\n"%(rowvalues['block_id'],\
									rowvalues['route_id'],\
									rowvalues['direction_id'],\
									rowvalues['trip_headsign'],\
									rowvalues['shape_id'],\
									rowvalues['service_id'],\
									rowvalues['trip_id']))

			addLines = addLines + 1
		
		#check
		print "   [*] Number of lines read from ", filename, ": %d" %currentLine	
		print "   [*] Number of lines written to ", newfilename, ": %d" %addLines	
		print "   [*] Done \n"

		#close down
		cvsfile.close()
		output.close()
		return tripsToRemove

	except Exception as ex:
		print "Exception with message:  %s!!" % str(ex)
		sys.exit(1)



def simplify_stop_times(newfilename, filename, trips):
	tripsInRecord = {}
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
		output.write("trip_id, stop_id, arrival_time, departure_time, stop_headsign\n")
		#print "trip_id, stop_id, arrival_time, departure_time, stop_headsign"
		
		print "   [*] Reading records "
		addLines = 0
		currentLine = 1
		for rowvalues in reader:
			currentLine = currentLine + 1
			stop_id = rowvalues['stop_id'] #.strip(), will slow down a lot
			trip_id = rowvalues['trip_id'] #.strip()
			arrival_time = rowvalues['arrival_time']
			departure_time = rowvalues['departure_time']		
			stop_headsign = rowvalues['stop_headsign']
			if trip_id in trips:
				continue

			output.write("%s, %s, %s, %s, %s\n"%(trip_id, stop_id, arrival_time, departure_time, stop_headsign))
			tripsInRecord[trip_id] = 1

			addLines = addLines + 1
		
		#check
		print "   [*] Number of lines read from ", filename, ": %d" %currentLine	
		print "   [*] Number of lines written to ", newfilename, ": %d" %addLines	
		print "   [*] Done \n"

		#close down
		cvsfile.close()
		output.close()
		return tripsInRecord

	except Exception as ex:
		print "Exception with message:  %s!!" % str(ex)
		sys.exit(1)

if __name__ == '__main__':
	services = simplify_calendar('calendar.txt', 'calendar_origin.txt', '20091215', '20100114' )
	services = simplify_calendar_dates('calendar_dates.txt', 'calendar_dates_origin.txt', services, '20091215', '20100114' )
	trips = simplify_trips('trips_new2.txt', 'trips_new.txt', services)
	tripsInRecord = simplify_stop_times('stop_times.txt', 'stop_times_new.txt', trips)
	tripsRemoved = remove_unused_trips('trips.txt', 'trips_new2.txt', tripsInRecord)
	print tripsRemoved


