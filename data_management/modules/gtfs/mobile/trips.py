#!/usr/bin/python
#
#  add_trips.py
#  
#
#  Created by Zhenwang Yao on 03/11/08.
#  Copyright (c) 2008 Music Motion. All rights reserved.
#

## This module import trips.txt to table 'trips' in a sqlite database
# 
# It take two parameters, as
#      import_trips $dbName $cvsFile
#
# Thus, it imports $cvsFile (trips.txt) to $dbName.trips.
#      if $dbName.trips exists, it deletes the table first.
#
# $dbName.trips table structure: 
#	   trip_id CHAR(64),
#	   route_id CHAR(64),
#	   service_id CHAR(64),
#	   direction_id CHAR(16),
#	   block_id CHAR(16),
#	   trip_headsign CHAR(128),
#
import csv
import sqlite3
import sys
import string
import os

def import_trips(dbname, filename, action):
	if action=="-append":
		print "   Appending %s into %s.trips" %(filename,dbname)
	elif action=="-update":
		print "   Updating %s into %s.trips" %(filename,dbname)
	elif action=="-refresh":
		print "   Converting %s into %s.trips" %(filename,dbname)
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
			print "   [*] Dropping table trips, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS trips")
			cursor.execute ("""CREATE TABLE trips (
							trip_id CHAR(64) PRIMARY KEY,
							route_id CHAR(64),
							service_id CHAR(64),
							direction_id CHAR(16),
							block_id CHAR(16),
							trip_headsign CHAR(128)
							)
						""")
			print "   [*] Table trips dropped, and a new one created."

		#insert record
		print "   [*] Opening file %s " % filename
		cvsfile = open(filename)
		headerreader = csv.reader(cvsfile,skipinitialspace=True)
		fieldnames = headerreader.next()
		reader = csv.DictReader(cvsfile, fieldnames, restkey='unknown', restval='',skipinitialspace=True)
		#print fieldnames

		print "   [*] Adding records into %s.trips " % dbname
		addLines = 0
		for rowvalues in reader:
			route_id = rowvalues['route_id'] #.strip(), will slow down a lot
			service_id = rowvalues['service_id'] #.strip()
			trip_id = rowvalues['trip_id'].strip()
			try:
				direction_id = rowvalues['direction_id']
			except:
				direction_id = ''
			try:
				block_id = rowvalues['block_id']
			except:
				block_id = ''
			try:
				trip_headsign = rowvalues['trip_headsign']
			except:
				trip_headsign = ''			  
			if action == "-update":						 
				cursor.execute("""
						INSERT OR REPLACE INTO trips (route_id,service_id,trip_id,direction_id,block_id,trip_headsign)
						VALUES
						(?, ?, ?, ?, ?, ?)
						""", (route_id,service_id,trip_id,direction_id,block_id,trip_headsign))
			else:
				cursor.execute("""
						INSERT INTO trips (route_id,service_id,trip_id,direction_id,block_id,trip_headsign)
						VALUES
						(?, ?, ?, ?, ?, ?)
						""", (route_id,service_id,trip_id,direction_id,block_id,trip_headsign))
							
			addLines = addLines + 1
		
		#check
		print "   [*] Number of lines read from ", filename, ": %d" %addLines	
		print "   [*] Checking imported %s.trips" % dbname
		cursor.execute("SELECT COUNT(*) FROM trips")
		print "   [*] Number of row in the table: ", cursor.fetchone()[0]
		print "   [*] Done \n"

		#close down
		cursor.close()
		cvsfile.close()

	except Exception, err:
		print "Error occured during importing (at Line %d), with error: %s!!" %(addLines, str(err))
		print ""
		sys.exit(1)		

	conn.close()
def refresh(dbname, filename):
	import_trips(dbname, filename, "-refresh")
	
def append(dbname, filename):
	import_trips(dbname, filename, "-append")
