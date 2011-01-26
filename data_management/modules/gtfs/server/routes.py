#! /usr/bin/python
## This module import routes.txt to table 'routes' in a mySQL database
# 
# It take two parameters, as
#	   import_routes $dbName $cvsFilePath
#
# Thus, it imports $cvsFilePath/routes.txt to $dbName.routes.
#	   if $dbName.routes exists, it deletes the table first.
#
# $dbName.routes table structure: 
#	   route_id CHAR(64) PRIMARY KEY,
#	   route_short_name CHAR(32),
#	   route_long_name CHAR(128),
#	   route_type CHAR(10)
#
import csv
import MySQLdb
import sys
import string
import os

def import_routes(dbhost, dbuser, dbpass, dbname, filename, action):
	if action=="-append":
		print "Appending %s into %s.routes" %(filename,dbname)
	else:
		print "Converting %s into %s.routes" %(filename,dbname)
	
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
			print "   [*] Dropping table routes, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS routes")
			cursor.execute ("""CREATE TABLE routes (
							route_id CHAR(64) PRIMARY KEY,
							route_short_name CHAR(32),
							route_long_name CHAR(128),
							route_type CHAR(10)
							)
						""")
			print "   [*] Table routes dropped, and a new one created."
			
		
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
			
			print "   [*] Adding records into %s.routes " % dbname
			addLines = 0
			for rowvalues in reader:
				route_id = rowvalues['route_id'].strip()
				route_short_name = rowvalues['route_short_name'].replace('&', '&amp;')
				route_long_name = rowvalues['route_long_name'].replace('&', '&amp;')
				route_type = rowvalues['route_type']
				if action == "-update":
					cursor.execute("""
							INSERT INTO routes (route_id,route_short_name,route_long_name, route_type)
							VALUES
							(%s, %s, %s, %s)
							ON DUPLICATE KEY UPDATE 
							route_id=%s,route_short_name=%s,route_long_name=%s, route_type=%s
							""", (route_id,route_short_name,route_long_name, route_type, route_id,route_short_name,route_long_name, route_type))
				else:
					cursor.execute("""
							INSERT INTO routes (route_id,route_short_name,route_long_name, route_type)
							VALUES
							(%s, %s, %s, %s)
							""", (route_id,route_short_name,route_long_name, route_type))
				addLines = addLines + 1
			cvsfile.close()
					
			#check
			print "   [*] Number of lines read from ", filename, ": %d" %addLines	 
			
		print "   [*] Checking imported %s.routes" % dbname
		cursor.execute("SELECT COUNT(*) FROM routes")	 
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
	import_routes(dbhost, dbuser, dbpass, dbname, filename, "-refresh")
	
def append(dbhost, dbuser, dbpass, dbname, filename):
	import_routes(dbhost, dbuser, dbpass, dbname, filename, "-append")
