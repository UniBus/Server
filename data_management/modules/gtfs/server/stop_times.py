#! /usr/bin/python
## This module import stop_times.txt to table 'stop_times' in a mySQL database
# 
# It take two parameters, as
#	   import_stop_times $dbName $cvsFilePath
#
# Thus, it imports $cvsFilePath/stop_times.txt to $dbName.stop_times.
#	   if $dbName.stop_times exists, it deletes the table first.
#
# $dbName.stop_times table structure: 
#	   trip_id CHAR(64),
#	   stop_id CHAR(32),
#	   arrival_time CHAR(64),
#	   departure_time CHAR(64),
#	   stop_headsign CHAR(64),
#
#  and since this is normally the table that has most records,
#  an index on stop_id is created (should I put trip_id into index as well?)
#
import csv
import MySQLdb
import sys
import string
import os
import time

def import_stop_times(dbhost, dbuser, dbpass, dbname, filename, action):
	if action=="-append":
		print "Appending %s into %s.stop_times" %(filename,dbname)
	else:
		print "Converting %s into %s.stop_times" %(filename,dbname)
		
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
			print "   [*] Dropping table stop_times, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS stop_times")
			cursor.execute ("""CREATE TABLE stop_times (
							trip_id CHAR(64),
							stop_id CHAR(32),
							arrival_time CHAR(64),
							departure_time CHAR(64),
							stop_headsign CHAR(64),
							INDEX stop_id USING HASH (stop_id),
							INDEX trip_id USING HASH (trip_id)						  
							)
						""")
			print "   [*] Table stop_times dropped, and a new one created."
			
		
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
		
			print "   [*] Adding records into %s.stop_times " % dbname
			addLines = 0
			currentLine = 1   #starting with 1 because of the header
			for rowvalues in reader:
				currentLine = currentLine + 1
				stop_id = rowvalues['stop_id'].replace(' ', '') #.strip(), will slow down a lot
				#The .replace(x) slow down a lot, but there are a couple of cities whose stop_id contain whitespace.
		
				trip_id = rowvalues['trip_id'] #.strip()
				arrival_time_str = string.strip(rowvalues['arrival_time'])
				departure_time_str = string.strip(rowvalues['departure_time'])
				
				arrival_time = arrival_time_str.rjust(8, '0')
				departure_time = departure_time_str.rjust(8, '0')
				if arrival_time == "00000000":
					print "   [*] WARNING: Invalid arrival times around line ", currentLine
					continue
				
				try:
					stop_headsign = rowvalues['stop_headsign'].replace('&', '&amp;')
				except:
					stop_headsign = ''
				
				cursor.execute("""
							INSERT INTO stop_times (trip_id,arrival_time,departure_time,stop_id,stop_headsign)
							VALUES
							(%s, %s, %s, %s, %s)
							""", (trip_id,arrival_time,departure_time,stop_id,stop_headsign) )
				addLines = addLines + 1
			cvsfile.close()
				   
			#check
			print "   [*] Number of lines read from ", filename, ": %d" %addLines	 
			
		print "   [*] Checking imported %s.stop_times" % dbname
		cursor.execute("SELECT COUNT(*) FROM stop_times")	 
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
	import_stop_times(dbhost, dbuser, dbpass, dbname, filename, "-refresh")
	
def append(dbhost, dbuser, dbpass, dbname, filename):
	import_stop_times(dbhost, dbuser, dbpass, dbname, filename, "-append")
