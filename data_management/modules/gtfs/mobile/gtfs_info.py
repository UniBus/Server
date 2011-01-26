#!/usr/bin/python
#
#  import_gtfs_info.py
#  
#
#  Created by Zhenwang Yao on 03/11/08.
#  Copyright (c) 2008 Music Motion. All rights reserved.
#

## This module updates 'cities' table in 'gtfs_info' database
#     to reflect changes for current supported cities.
# 
# It take two parameters, as
#      import_gtfs_info $dbName $cvsFile(supportedcities.lst)
#
# Thus, it imports $cvsFile to dbName.cities.
#      if dbName.cities exists, it deletes the table first.
#
# gtfs_info.cities table structure: 
#      id CHAR(32),              #city id
#      name CHAR(32),            #name, e.g. Portland
#      state CHAR(32),           #state, e.g. OR
#      country CHAR(32),         #country, e.g. USA
#      website CHAR(128),        #url for query
#      dbname CHAR(128),         #database name
#      lastupdate CHAR(16)       #time of last update
#      local INTEGER             #if database has been downloaded
#      oldbdownloaded INTEGER    #off-line database downloaded
#      oldbtime CHAR (16)        #off-line database download time
#
import csv
import sqlite3
import sys
import string
import os

def update_gtfs_info(dbname, filename):
	print "   Converting ", filename, " into ", dbname

	try:
		#create table
		print "   [*] Connecting to database %s." %dbname
		conn = sqlite3.connect(dbname, isolation_level=None)
		cursor = conn.cursor()
		print "   [*] Connected to database."

		print "   [*] Dropping table cities, and creating a new one."
		cursor.execute ("DROP TABLE IF EXISTS cities")
		cursor.execute ("""CREATE TABLE IF NOT EXISTS cities (
						id CHAR(32) PRIMARY KEY,
						name CHAR(32),				
						state CHAR(32),
						country CHAR(32),
						website CHAR(128),
						dbname CHAR(128),
						lastupdate CHAR(16),
						local INTEGER,
						oldbdownloaded INTEGER,
						oldbtime CHAR(16)
						)
						""")		
		print "   [*] Table cities dropped, and a new one created."
	
		#insert record
		cvsfile = open(filename)
		headerreader = csv.reader(cvsfile,skipinitialspace=True)
		fieldnames = headerreader.next()
		reader = csv.DictReader(cvsfile, fieldnames, restkey='unknown', restval='',skipinitialspace=True)
		#print fieldnames

		print "   [*] Adding records into %s " % dbname
		addLines = 0;
		for rowvalues in reader:
			cursor.execute("""
					INSERT INTO cities (id, name, state, country, website, dbname, lastupdate, local, oldbdownloaded, oldbtime)
					VALUES
					(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
					""", (rowvalues['id'], rowvalues['name'], rowvalues['state'], rowvalues['country'], rowvalues['website'], rowvalues['dbname'], rowvalues['lastupdate'], rowvalues['local'], rowvalues['oldbdownloaded'], rowvalues['oldbtime']))
			addLines = addLines + 1
			
		#check
		#check
		#print "   [*] Comitting changes "
		print "   [*] Number of lines read from ", filename, ": %d" %addLines	
		print "   [*] Checking imported %s.cities" % dbname
		cursor.execute("SELECT COUNT(*) FROM cities")
		print "   [*] Number of row in the table: ", cursor.fetchone()[0]
		print "   [*] Done \n"

		#close down
		cursor.close()
		cvsfile.close()

	except Exception, err:
		print "Error occured during importing (at Line %d), with error: %s!!" %(addLines, str(err))
		sys.exit(1)		

	conn.commit()
	conn.close()

def update(dbname, filename):
	update_gtfs_info(dbname, filename)
