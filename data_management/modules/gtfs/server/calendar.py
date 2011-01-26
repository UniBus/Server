#! /usr/bin/python
## This module import calendar.txt to table 'calendar' in a mySQL database
# 
# It take two parameters, as
#	   import_calendar $dbName $cvsFilePath
#
# Thus, it imports $cvsFilePath/calendar.txt to $dbName.calendar.
#	   if $dbName.calendar exists, it deletes the table first.
#
# $dbName.calendar table structure: 
#	   service_id CHAR(64) PRIMARY KEY, 					   
#	   monday INT,
#	   tuesday INT,
#	   wednesday INT,
#	   thursday INT,
#	   friday INT,
#	   saturday INT,
#	   sunday INT,
#	   start_date CHAR(32),
#	   end_date CHAR(32)						
#
import csv
import MySQLdb
import sys
import string
import os

def import_calendar(dbhost, dbuser, dbpass, dbname, filename, action):
	if action=="-append":
		print "Appending %s into %s.calendar" %(filename,dbname)
	else:
		print "Converting %s into %s.calendar" %(filename,dbname)
	
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
			print "   [*] Dropping table calendar, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS calendar")
			cursor.execute ("""CREATE TABLE calendar (
							service_id CHAR(64) PRIMARY KEY,						
							monday INT,
							tuesday INT,
							wednesday INT,
							thursday INT,
							friday INT,
							saturday INT,
							sunday INT,
							start_date CHAR(32),
							end_date CHAR(32)						 
							)
						""")
			print "   [*] Table calendar dropped, and a new one created."
			
		
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
			
			print "   [*] Adding records into %s.calendar " % dbname
			addLines = 0
			for rowvalues in reader:
				if action == "-update":
					cursor.execute("""
					INSERT INTO calendar (service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date)
					VALUES
					(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
					ON DUPLICATE KEY UPDATE 
					service_id=%s,monday=%s,tuesday=%s,wednesday=%s,thursday=%s,friday=%s,saturday=%s,sunday=%s,start_date=%s,end_date=%s
					""", (rowvalues['service_id'].strip(),rowvalues['monday'],rowvalues['tuesday'],rowvalues['wednesday'],rowvalues['thursday'],rowvalues['friday'],rowvalues['saturday'],rowvalues['sunday'],rowvalues['start_date'],rowvalues['end_date'],rowvalues['service_id'].strip(),rowvalues['monday'],rowvalues['tuesday'],rowvalues['wednesday'],rowvalues['thursday'],rowvalues['friday'],rowvalues['saturday'],rowvalues['sunday'],rowvalues['start_date'],rowvalues['end_date']) )
				else:
					cursor.execute("""
					INSERT INTO calendar (service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date)
					VALUES
					(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
					""", (rowvalues['service_id'].strip(),rowvalues['monday'],rowvalues['tuesday'],rowvalues['wednesday'],rowvalues['thursday'],rowvalues['friday'],rowvalues['saturday'],rowvalues['sunday'],rowvalues['start_date'],rowvalues['end_date']) )
				addLines = addLines + 1
			cvsfile.close()
					
			#check
			print "   [*] Number of lines read from ", filename, ": %d" %addLines	
		
		print "   [*] Checking imported %s.calendar" % dbname
		cursor.execute("SELECT COUNT(*) FROM calendar")    
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
	import_calendar(dbhost, dbuser, dbpass, dbname, filename, "-refresh")
	
def append(dbhost, dbuser, dbpass, dbname, filename):
	import_calendar(dbhost, dbuser, dbpass, dbname, filename, "-append")
