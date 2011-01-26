#! /usr/bin/python
## This module import calendar_dates.txt to table 'calendar_dates' in a mySQL database
# 
# It take two parameters, as
#	   import_calendar_dates $dbName $cvsFilePath
#
# Thus, it imports $cvsFilePath/calendar_dates.txt to $dbName.calendar_dates.
#	   if $dbName.calendar_dates exists, it deletes the table first.
#
# $dbName.calendar_dates table structure: 
#	   service_id CHAR(64),
#	   date CHAR(32),
#	   exception_type CHAR(8)
#
import csv
import MySQLdb
import sys
import string
import os

def import_calendar_dates(dbhost, dbuser, dbpass, dbname, filename, action):
	if action=="-append":
		print "Appending %s into %s.calendar_dates" %(filename,dbname)
	else:
		print "Converting %s into %s.calendar_dates" %(filename,dbname)
	
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
			print "   [*] Dropping table calendar_dates, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS calendar_dates")
			cursor.execute ("""CREATE TABLE calendar_dates (
							service_id CHAR(64),
							date CHAR(32),
							exception_type CHAR(8)
							)
						""")
			print "   [*] Table calendar_dates dropped, and a new one created."
			
		
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
			
			print "   [*] Adding records into %s.calendar_dates " % dbname
			addLines = 0
			for rowvalues in reader:
				service_id = rowvalues['service_id'].strip()
				date = rowvalues['date']
				exception_type = rowvalues['exception_type']
				cursor.execute("""
							INSERT INTO calendar_dates (service_id,date,exception_type)
							VALUES
							(%s, %s, %s)
							""", (service_id,date,exception_type) )
				addLines = addLines + 1
			cvsfile.close()
			
			#check
			print "   [*] Number of lines read from ", filename, ": %d" %addLines	 
						
		print "   [*] Checking imported %s.calendar_dates" % dbname
		cursor.execute("SELECT COUNT(*) FROM calendar_dates")	 			
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
	import_calendar_dates(dbhost, dbuser, dbpass, dbname, filename, "-refresh")
	
def append(dbhost, dbuser, dbpass, dbname, filename):
	import_calendar_dates(dbhost, dbuser, dbpass, dbname, filename, "-append")
