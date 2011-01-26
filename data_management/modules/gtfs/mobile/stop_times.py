#!/usr/bin/python
#
#  add_stops.py
#  
#
#  Created by Zhenwang Yao on 03/11/08.
#  Copyright (c) 2008 Music Motion. All rights reserved.
#

## This module import stops.txt to table 'stops' in a sqlite database
# 
# It take two parameters, as
#	   import_stops $dbName $cvsFile
#
# Thus, it imports $cvsFile (stops.txt) to $dbName.stops.
#	   if $dbName.stops exists, it deletes the table first.
#
# $dbName.stop_times table structure: 
#      trip_id CHAR(64),
#      stop_id CHAR(32),
#      arrival_time CHAR(64),
#      stop_headsign CHAR(64),
#
import csv
import sqlite3
import sys
import string
import os

def import_stop_times(dbname, filename, action):
	if action=="-append":
		print "   Appending %s into %s.stop_times" %(filename,dbname)
	elif action=="-update":
		print "   Updating %s into %s.stop_times" %(filename,dbname)
	elif action=="-refresh":
		print "   Converting %s into %s.stop_times" %(filename,dbname)
	else:
		print "   Wrong action[%s] argument!" %action
		sys.exit(1)

	try:
		#create table
		print "   [*] Connecting to database %s." %dbname
		conn = sqlite3.connect(dbname, isolation_level=None)
		cursor = conn.cursor()
		print "   [*] Connected to database."

		if action == "-refresh":
			print "   [*] Dropping table stop_times, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS stop_times")
			cursor.execute ("""CREATE TABLE stop_times (
							trip_id CHAR(64),
							stop_id CHAR(32),
							arrival_time CHAR(64),
							stop_headsign CHAR(64)
							)
				""")	
		
			print "   [*] Create stop_index ON stop_times"		
			cursor.execute ("CREATE INDEX stop_index ON stop_times(stop_id)")
			print "   [*] Create trip_index ON stop_times"		
			cursor.execute ("CREATE INDEX trip_index ON stop_times(trip_id)")
			print "   [*] Table stop_times dropped, and a new one created."


		#insert record
		print "   [*] Opening file %s " % filename
		cvsfile = open(filename)
		headerreader = csv.reader(cvsfile,skipinitialspace=True)
		fieldnames = headerreader.next()
		reader = csv.DictReader(cvsfile, fieldnames, restkey='unknown', restval='',skipinitialspace=True)
		#print fieldnames

		print "   [*] Adding records into %s.stop_times " %dbname
		addLines = 0
		currentLine = 1
		for rowvalues in reader:
			currentLine = currentLine + 1
			stop_id = rowvalues['stop_id'].replace(' ', '') #.strip(), will slow down a lot
			trip_id = rowvalues['trip_id'] #.strip()
			arrival_time_str = string.strip(rowvalues['arrival_time'])
			departure_time_str = string.strip(rowvalues['departure_time'])
		
			arrival_time = arrival_time_str.rjust(8, '0')
			departure_time = departure_time_str.rjust(8, '0')
			if arrival_time == "00000000":
				print "   [*] WARNING: Invalid arrival times around line ", currentLine
				continue

			try:
				stop_headsign = rowvalues['stop_headsign']
			except:
				stop_headsign = ''
		
			if action == "-update":
				cursor.execute("""
					INSERT OR REPLACE INTO stop_times (trip_id,arrival_time,stop_id,stop_headsign)
					VALUES
					(?, ?, ?, ?)
					""", (trip_id,arrival_time,stop_id,stop_headsign)  )
			else:
				cursor.execute("""
					INSERT INTO stop_times (trip_id,arrival_time,stop_id,stop_headsign)
					VALUES
					(?, ?, ?, ?)
					""", (trip_id,arrival_time,stop_id,stop_headsign) )

			addLines = addLines + 1
		
		#check
		print "   [*] Number of lines read from ", filename, ": %d" %addLines	
		print "   [*] Checking imported %s.stop_times" % dbname
		cursor.execute("SELECT COUNT(*) FROM stop_times")
		print "   [*] Number of row in the table: ", cursor.fetchone()[0]
		print "   [*] Done \n"

		#close down
		cursor.close()
		cvsfile.close()

	except Exception, err:
		print "Error occured during importing (at Line %d), with error: %s!!" %(addLines, str(err))
		sys.exit(1) 	

	conn.close()

def refresh(dbname, filename):
	import_stop_times(dbname, filename, "-refresh")
	
def append(dbname, filename):
	import_stop_times(dbname, filename, "-append")
