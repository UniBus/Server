#! /usr/bin/python
## This module import trips.txt to table 'trips' in a mySQL database
# 
# It take two parameters, as
#	   import_trips $dbName $cvsFilePath
#
# Thus, it imports $cvsFilePath/trips.txt to $dbName.trips.
#	   if $dbName.trips exists, it deletes the table first.
#
# $dbName.trips table structure: 
#	   trip_id CHAR(64),
#	   route_id CHAR(64),
#	   service_id CHAR(64),
#	   direction_id CHAR(16),
#	   block_id CHAR(16),
#	   trip_headsign CHAR(128),
#	   shape_id CHAR(16),
#
#  this table may also contains a fair number of record, so
#	an index is created on trip_id
#
import csv
import MySQLdb
import sys
import string
import os

def import_trips(dbhost, dbuser, dbpass, dbname, filename, action):
	if action=="-append":
		print "Appending %s into %s.trips" %(filename,dbname)
	else:
		print "Converting %s into %s.trips" %(filename,dbname)
	
	try:
		#create database if it doesn't exist
		#call create_db.py to create if needed
		
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
		if action == "-refresh":
			print "   [*] Dropping table trips, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS trips")
			cursor.execute ("""CREATE TABLE trips (
							trip_id CHAR(64),
							route_id CHAR(64),
							service_id CHAR(64),
							direction_id CHAR(16),
							block_id CHAR(16),
							trip_headsign CHAR(128),
							shape_id CHAR(16),
							INDEX trip_id USING HASH (trip_id)
							)
						""")
			print "   [*] Table trips dropped, and a new one created."
			
		
		if not os.path.exists(filename):
			print "   [*] WARNING: %s does not exist." %filename
		else:
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
					trip_headsign = rowvalues['trip_headsign'].replace('&', '&amp;')
				except:
					trip_headsign = ''			  
				try:
					shape_id = rowvalues['shape_id']
				except:
					shape_id = ''			 
				cursor.execute("""
							INSERT INTO trips (route_id,service_id,trip_id,direction_id,block_id,trip_headsign,shape_id)
							VALUES
							(%s, %s, %s, %s, %s, %s, %s)
							""", (route_id,service_id,trip_id,direction_id,block_id,trip_headsign,shape_id))
				addLines = addLines + 1
			cvsfile.close()
					
			#check
			print "   [*] Number of lines read from ", filename, ": %d" %addLines
			
		print "   [*] Checking imported %s.trips" % dbname
		cursor.execute("SELECT COUNT(*) FROM trips")	
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
	import_trips(dbhost, dbuser, dbpass, dbname, filename, "-refresh")
	
def append(dbhost, dbuser, dbpass, dbname, filename):
	import_trips(dbhost, dbuser, dbpass, dbname, filename, "-append")
