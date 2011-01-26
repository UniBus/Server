#! /usr/bin/python
## This module import stops.txt to table 'stops' in a mySQL database
# 
# It take two parameters, as
#	   import_stops $dbName $cvsFilePath
#
# Thus, it imports $cvsFilePath/stops.txt to $dbName.stops.
#	   if $dbName.stops exists, it deletes the table first.
#
# $dbName.stops table structure: 
#	   stop_id CHAR(32) PRIMARY KEY,
#	   stop_name CHAR(100),
#	   stop_lat DOUBLE,
#	   stop_lon DOUBLE,
#	   stop_desc CHAR(128)
#
import csv
import MySQLdb
import sys
import string
import os

def import_stops(dbhost, dbuser, dbpass, dbname, filename, action):
	if action=="-append":
		print "Appending %s into %s.stops" %(filename,dbname)
	else:
		print "Converting %s into %s.stops" %(filename,dbname)
	
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
			print "   [*] Dropping table stops, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS stops")
			cursor.execute ("""CREATE TABLE stops (
							stop_id CHAR(32) PRIMARY KEY,
							stop_name CHAR(100),
							stop_lat DOUBLE,
							stop_lon DOUBLE,
							stop_desc CHAR(128)
							)
						""")
			print "   [*] Table stops dropped, and a new one created."
			
		
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
			
			print "   [*] Adding records into %s.stops" % dbname
			addLines = 0
			for rowvalues in reader:
				stop_id = rowvalues['stop_id'].replace(' ', '') #.strip(), will slow down a lot
				#The .replace(x) slow down a lot, but there are a couple of cities whose stop_id contain whitespace.
		
				stop_name = rowvalues['stop_name'].replace('&', '&amp;')
				try:
					stop_lat = rowvalues['stop_lat']
				except:
					stop_lat = 0
				try:		
					stop_lon = rowvalues['stop_lon']
				except:
					stop_lon = 0
				try:
					stop_desc = rowvalues['stop_desc']
				except:
					stop_desc =  ''
		
				if action == "-update":
					cursor.execute("""
							INSERT INTO stops (stop_id, stop_name, stop_lat, stop_lon, stop_desc)
							VALUES
							(%s, %s, %s, %s, %s)
							ON DUPLICATE KEY UPDATE 
							stop_id=%s, stop_name=%s, stop_lat=%s, stop_lon=%s, stop_desc=%s
							""", (stop_id, stop_name, stop_lat, stop_lon, stop_desc, stop_id, stop_name, stop_lat, stop_lon, stop_desc))
							
				else:
					#if addLines == 0:
					#	print "INSERT INTO stops (stop_id, stop_name, stop_lat, stop_lon, stop_desc) VALUES (%s, %s, %s, %s, %s)" %(stop_id, stop_name, stop_lat, stop_lon, stop_desc)
					#print (stop_id, stop_name, stop_lat, stop_lon, stop_desc), "\n"
					#Notes:
					#	Data truncation error, may be caused by trailing whitespaces
					cursor.execute("""
							INSERT INTO stops (stop_id, stop_name, stop_lat, stop_lon, stop_desc)
							VALUES
							(%s, %s, %s, %s, %s)
							""", (stop_id, stop_name, stop_lat, stop_lon, stop_desc))
									
				addLines = addLines + 1
			cvsfile.close()
					
			#check
			print "   [*] Number of lines read from ", filename, ": %d" %addLines
			 
		print "   [*] Checking imported %s.stops" % dbname
		cursor.execute("SELECT COUNT(*) FROM stops")	
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
	import_stops(dbhost, dbuser, dbpass, dbname, filename, "-refresh")
	
def append(dbhost, dbuser, dbpass, dbname, filename):
	import_stops(dbhost, dbuser, dbpass, dbname, filename, "-append")
