#!/usr/bin/python
#
#  add_routes.py
#  
#
#  Created by Zhenwang Yao on 03/11/08.
#  Copyright (c) 2008 Music Motion. All rights reserved.
#

## This module import routes.txt to table 'routes' in a sqlite database
# 
# It take two parameters, as
#      import_routes $dbName $cvsFile
#
# Thus, it imports $cvsFile (routes.txt) to $dbName.routes.
#      if $dbName.routes exists, it deletes the table first.
#
# $dbName.routes table structure: 
#      route_id CHAR(16) PRIMARY KEY, 
#      route_short_name CHAR(64),
#      route_long_name CHAR(128),
#
import csv
import sqlite3
import sys
import string
import os

def import_routes(dbname, filename, action):
	if action=="-append":
		print "   Appending %s into %s.routes" %(filename,dbname)
	elif action=="-update":
		print "   Updating %s into %s.routes" %(filename,dbname)
	elif action=="-refresh":
		print "   Converting %s into %s.routes" %(filename,dbname)
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
			print "   [*] Dropping table routes, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS routes")
			cursor.execute ("""CREATE TABLE routes (
				route_id CHAR(16) PRIMARY KEY, 
				route_short_name CHAR(64),
				route_long_name CHAR(128),
				route_type INTEGER
				)
				""")	
			print "   [*] Table routes dropped, and a new one created."

		#insert record
		print "   [*] Opening file %s " % filename
		cvsfile = open(filename)
		headerreader = csv.reader(cvsfile,skipinitialspace=True)
		fieldnames = headerreader.next()
		reader = csv.DictReader(cvsfile, fieldnames, restkey='unknown', restval='',skipinitialspace=True)
		#print fieldnames

		print "   [*] Adding records into %s " % dbname
		addLines = 0;
		for rowvalues in reader:
			route_id = rowvalues['route_id'].strip()
			route_short_name = rowvalues['route_short_name'] 
			route_long_name = rowvalues['route_long_name']
			route_type = rowvalues['route_type']
		
			#print route_id,route_short_name,route_long_name
			if action == "-update":
				cursor.execute("""
						INSERT OR REPLACE INTO routes (route_id,route_short_name,route_long_name, route_type)
						VALUES
						(?, ?, ?, ?)
						""", (route_id,route_short_name,route_long_name, route_type))
			else:
				cursor.execute("""
						INSERT INTO routes (route_id,route_short_name,route_long_name, route_type)
						VALUES
						(?, ?, ?, ?)
						""", (route_id,route_short_name,route_long_name, route_type))
			#print route_id
			addLines = addLines + 1
		
		#check
		print "   [*] Number of lines read from ", filename, ": %d" %addLines	
		print "   [*] Checking imported %s.routes" % dbname
		cursor.execute("SELECT COUNT(*) FROM routes")
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
	import_routes(dbname, filename, "-refresh")
	
def append(dbname, filename):
	import_routes(dbname, filename, "-append")
