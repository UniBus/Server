#! /usr/bin/python
## This module import agenency.txt to table 'agency' in a mySQL database
# 
# It take two parameters, as
#	   import_agency $dbName $cvsFilePath
#
# Thus, it imports $cvsFilePath/agency.txt to $dbName.agency.
#	   if $dbName.agency exists, it deletes the table first.
#
# $dbName.agency table structure: 
#	   agency_name CHAR(128),
#	   agency_timezone CHAR(128)
#
import csv
import MySQLdb
import sys
import string
import os

def import_agency(dbhost, dbuser, dbpass, dbname, filename, action):
	if action=="-append":
		print "Appending %s into %s.agency" %(filename,dbname)
	else:
		print "Converting %s into %s.agency" %(filename,dbname)

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
			print "   [*] Dropping table agency, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS agency")
			cursor.execute ("""CREATE TABLE agency (
							agency_name CHAR(128),
							agency_timezone CHAR(128)
							)
						""")
			print "   [*] Table agency dropped, and a new one created."
			
		
		if not os.path.exists(filename):
			print "   [*] WARNING: %s does not exist." %filename
		else:
			#insert record
			print "   [*] Opening file %s " % filename
			addLines = 0
			cvsfile = open(filename)
			headerreader = csv.reader(cvsfile,skipinitialspace=True)
			fieldnames = headerreader.next()
			reader = csv.DictReader(cvsfile, fieldnames, restkey='unknown', restval='',skipinitialspace=True)
			#print fieldnames
			
			print "   [*] Adding records into %s.agency " % dbname
			for rowvalues in reader:
				cursor.execute("""
						INSERT INTO agency (agency_name, agency_timezone)
						VALUES
						(%s, %s)
						""", (rowvalues['agency_name'], rowvalues['agency_timezone']))
				addLines = addLines + 1
			cvsfile.close()
					
			#check
			print "   [*] Number of lines read from ", filename, ": %d" %addLines	 
			
		print "   [*] Checking imported %s.agency" % dbname
		cursor.execute("SELECT COUNT(*) FROM agency")	 
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
	import_agency(dbhost, dbuser, dbpass, dbname, filename, "-refresh")
	
def append(dbhost, dbuser, dbpass, dbname, filename):
	import_agency(dbhost, dbuser, dbpass, dbname, filename, "-append")
