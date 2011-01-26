#! /usr/bin/python
## This module updates 'cities' table in 'gtfs_info' database
#	  to reflect changes for current supported cities.
# 
# It take two parameters, as
#	   update_gtfs_info $cvsFile(supportedcities.lst)
#
# Thus, it imports $cvsFile to gtfs_info.cities.
#	   if gtfs_info.cities exists, it deletes the table first.
#
# gtfs_info.cities table structure: 
#	   id CHAR(32), 			 #city id
#	   name CHAR(32),			 #name, e.g. Portland
#	   state CHAR(32),			 #state, e.g. OR
#	   country CHAR(32),		 #country, e.g. USA
#	   website CHAR(128),		 #url for query
#	   dbname CHAR(128),		 #database name
#	   lastupdate CHAR(16)		 #time of last update
#
import csv
import MySQLdb
import sys
import string
import os

def import_gtfs_info(dbhost, dbuser, dbpass, dbname, filename, action):
	print "Converting %s into %s.cities" % (filename, dbname)
	
	try:
		#create database if it doesn't exist
		conn = MySQLdb.connect(host = dbhost,
							   user = dbuser,
							   passwd = dbpass)
		cursor = conn.cursor()
		cursor.execute("""CREATE DATABASE IF NOT EXISTS """ + dbname)
		conn.commit()
		conn.close()		
	except MySQLdb.Error, e:
		print "Error %d %s" % (e.args[0], e.args[1])
	
	try:
		#connect to the database
		print "   [*] Connecting to database %s." %dbname
		conn = MySQLdb.connect(host = dbhost,
							   user = dbuser,
							   passwd = dbpass,
							   db = dbname) 	   
		print "   [*] Connected to database."
		
	except MySQLdb.Error, e:
		print "Error %d %s\n" % (e.args[0], e.args[1])
		sys.exit(1) 	   
		
	try:
		#create table
		cursor = conn.cursor()
		print "   [*] Dropping table cities, and creating a new one."
		cursor.execute ("DROP TABLE IF EXISTS cities")
		cursor.execute ("""CREATE TABLE IF NOT EXISTS cities (
							id CHAR(32),			  #city id
							name CHAR(32),				  
							state CHAR(32),
							country CHAR(32),
							website CHAR(128),
							dbname CHAR(128),
							lastupdate CHAR(16), 	  #time of last update
							oldbtime CHAR(16) 		  #time of off-line database
							)
						""")
		print "   [*] Table cities dropped, and a new one created."
		
		if not os.path.exists(filename):
			print "   [*] WARNING: %s does not exist." %filename
		else:
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
						INSERT INTO cities (id, name, state, country, website, dbname, lastupdate, oldbtime)
						VALUE
						(%s, %s, %s, %s, %s, %s, %s, %s)
						""", (rowvalues['id'], rowvalues['name'], rowvalues['state'], rowvalues['country'], rowvalues['website'], rowvalues['dbname'], rowvalues['lastupdate'], rowvalues['oldbtime']))
				addLines = addLines + 1
			cvsfile.close()
					
			#check
			print "   [*] Number of lines read from ", filename, ": %d" %addLines
			
		print "   [*] Checking imported %s.cities" % dbname
		cursor.execute("SELECT COUNT(*) FROM cities")
		print "   [*] Number of row in the table: ", cursor.fetchone()[0]
		print "   [*] Done \n"
		
		#close down
		cursor.close()
	
	except MySQLdb.Error, e:
		print "Error %d %s\n" % (e.args[0], e.args[1])
		sys.exit(1) 	   
	
	conn.commit()
	conn.close()

def refresh(dbhost, dbuser, dbpass, dbname, filename):
	import_gtfs_info(dbhost, dbuser, dbpass, dbname, filename)
