#!/usr/bin/python
#
#  replace_stop_ids.py
#  
#
#  Created by Zhenwang Yao on 03/11/08.
#  Copyright (c) 2008 Music Motion. All rights reserved.
#

## This module import replace stop_id with stop_code in
#    - stops.txt, and
#    - stop_times.txt
#

import csv
import sys
import string
import os
from sets import Set

def update_stops(newfilename, filename):
	idsToCodes = {}
	codesToIds = {}
	directions = Set(['E', 'W', 'S', 'N'])
	try:
		print "   [*] Opening file %s reading" % filename
		cvsfile = open(filename)
		headerreader = csv.reader(cvsfile,skipinitialspace=True)
		fieldnames = headerreader.next()
		reader = csv.DictReader(cvsfile, fieldnames, restkey='unknown', restval='',skipinitialspace=True)
		#print fieldnames

		print "   [*] Opening file %s for writing" % newfilename
		output = open(newfilename, "w")
		output.write("stop_id, stop_name, stop_lat, stop_lon, stop_desc\n")

		print "   [*] Adding records into stop dictionary "
		addLines = 0
		currentLine = 1
		for rowvalues in reader:
			currentLine = currentLine + 1
			stop_id = rowvalues['stop_id'] #.strip(), will slow down a lot
			stop_code = rowvalues['stop_code'] #.replace('&', '&amp;')
			if len(stop_code) == 0:
				continue
			idsToCodes[stop_id] = stop_code

			# 			
			# A little bit tricky here.			
			# There might be multiple stop_id correspond to same stop_code,
			# and it doesn't necessary mean a duplications, in fact it means
			# stops are merged together
			# 
			# \TODO Ideally, the one with bigger stop_id should be used.
			#       but here, I didn't keep track of all correspondence.
			if stop_code in codesToIds:
				print "   [*] WARNING: Duplicated stop code: %s" % stop_code
				continue
			codesToIds[stop_code] = stop_id

			#print stop_code
			#print "%s, %s, %s, %s, %s\n" % (stop_code, rowvalues['stop_name'], rowvalues['stop_lat'], rowvalues['stop_lon'], rowvalues['stop_desc'] )
			stop_name = rowvalues['stop_name'].title()
			stop_desc = rowvalues['stop_desc'].title()

			stop_name = stop_name.replace("Nb ", "NB ")
			stop_name = stop_name.replace("Eb ", "EB ")
			stop_name = stop_name.replace("Wb ", "WB ")
			stop_name = stop_name.replace("Sb ", "SB ")
			stop_name = stop_name.replace("Sfu", "SFU")
			stop_name = stop_name.replace("Ubc", "UBC")
			stop_name = stop_name.replace("1St ", "1st ")
			stop_name = stop_name.replace("2Nd ", "2nd ")
			stop_name = stop_name.replace("3Rd ", "3rd ")
			stop_name = stop_name.replace(" Fs ", " FS ")
			stop_name = stop_name.replace(" Ns ", " NS ")

			stop_desc = stop_desc.replace("Sfu", "SFU")
			stop_desc = stop_desc.replace("Ubc", "UBC")
			stop_desc = stop_desc.replace("1St ", "1st ")
			stop_desc = stop_desc.replace("2Nd ", "2nd ")
			stop_desc = stop_desc.replace("3Rd ", "3rd ")

			output.write("%s, %s, %s, %s, %s\n" % (stop_code, stop_name, rowvalues['stop_lat'], rowvalues['stop_lon'], stop_desc ))
			#print stop_id
			addLines = addLines + 1
		
		#check
		print "   [*] Number of lines read from ", filename, ": %d" %currentLine	
		print "   [*] Number of lines written to ", newfilename, ": %d" %addLines	
		print "   [*] Done \n"

		output.close()
		cvsfile.close()
		return idsToCodes

	except Exception as ex:
		print "Exception with message:  %s!!" % str(ex)
		sys.exit(1)
	

def update_stop_times(newfilename, filename, stopdict):
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
			stop_headsign = rowvalues['stop_headsign'].title()
			if not stop_id in stopdict:
				#print "   [*] Warning: some stop skipped with id = %s. " % stop_id
				continue

			output.write("%s, %s, %s, %s, %s\n"%(trip_id, stopdict[stop_id], arrival_time, departure_time, stop_headsign))

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
	stopdict = update_stops('stops.txt', 'stops_origin.txt')
	#if '8672_merged_3399176' in stopdict:
	#	print stopdict['8672_merged_3399176']
	#else:
	#	print '8672_merged_3399176 does not exist'

	#if '8672_merged_3399212' in stopdict:
	#	print stopdict['8672_merged_3399212']
	#else:
	#	print '8672_merged_3399212 does not exist'

	#update_stop_times('stop_times_new.txt', 'stop_times_origin.txt', stopdict)


