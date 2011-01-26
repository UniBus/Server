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
#      import_stops $dbName $cvsFile
#
# Thus, it imports $cvsFile (stops.txt) to $dbName.stops.
#      if $dbName.stops exists, it deletes the table first.
#
# $dbName.stops table structure: 
#      stop_id CHAR(16) PRIMARY KEY,
#      stop_name CHAR(64),
#      stop_lat DOUBLE,
#      stop_lon DOUBLE,
#      stop_desc CHAR(128)
#
import csv
import sqlite3
import sys
import string
import os

def import_stops(dbname, filename, action):
	if action=="-append":
		print "   Appending %s into %s.stops" %(filename,dbname)
	elif action=="-update":
		print "   Updating %s into %s.stops" %(filename,dbname)
	elif action=="-refresh":
		print "   Converting %s into %s.stops" %(filename,dbname)
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
			print "   [*] Dropping table stops, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS stops")
			cursor.execute ("""CREATE TABLE stops (
				stop_id CHAR(16) PRIMARY KEY,
				stop_name CHAR(64),
				stop_lat DOUBLE,
				stop_lon DOUBLE,
				stop_desc CHAR(128)
				)
				""")	
			print "   [*] Table stops dropped, and a new one created."

		#insert record
		print "   [*] Opening file %s " % filename
		cvsfile = open(filename)
		headerreader = csv.reader(cvsfile,skipinitialspace=True)
		fieldnames = headerreader.next()
		reader = csv.DictReader(cvsfile, fieldnames, restkey='unknown', restval='',skipinitialspace=True)
		#print fieldnames

		print "   [*] Adding records into %s " % dbname
		addLines = 0
		for rowvalues in reader:
			stop_id = rowvalues['stop_id'].replace(' ', '') #.strip(), will slow down a lot
			stop_name = rowvalues['stop_name'] #.replace('&', '&amp;')
			stop_lat = rowvalues['stop_lat']
			stop_lon = rowvalues['stop_lon']
			try:
				stop_desc = rowvalues['stop_desc'].strip()
			except:
				stop_desc =  ''

			if stop_desc == '':
				stop_desc = stop_name

			#print stop_id, stop_name, stop_lat, stop_lon, stop_desc
			if action == "-update":
				cursor.execute("""
					INSERT OR REPLACE INTO stops (stop_id, stop_name, stop_lat, stop_lon, stop_desc)
					VALUES
					(?, ?, ?, ?, ?)
					""", (stop_id, stop_name, stop_lat, stop_lon, stop_desc))
			else:
				cursor.execute("""
					INSERT INTO stops (stop_id, stop_name, stop_lat, stop_lon, stop_desc)
					VALUES
					(?, ?, ?, ?, ?)
					""", (stop_id, stop_name, stop_lat, stop_lon, stop_desc))
			#print stop_id
			addLines = addLines + 1
		
		#check
		print "   [*] Number of lines read from ", filename, ": %d" %addLines	
		print "   [*] Checking imported %s.stops" % dbname
		cursor.execute("SELECT COUNT(*) FROM stops")
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
	import_stops(dbname, filename, "-refresh")
	
def append(dbname, filename):
	import_stops(dbname, filename, "-append")

