#! /usr/bin/python
## This module import shapes.txt to table 'shapes' in a mySQL database
# 
# It take two parameters, as
#	   import_shapes $dbName $cvsFilePath
#
# Thus, it imports $cvsFilePath/shapes.txt to $dbName.shapes.
#	   if $dbName.shapes exists, it deletes the table first.
#
# $dbName.shapes table structure: 
#	   shape_id CHAR(32),
#	   shape_pt_lat DOUBLE,
#	   shape_pt_lon DOUBLE,
#	   shape_pt_sequence INTEGER,
#	   INDEX shape_id USING HASH (shape_id)
#
#  this table may also contains a fair number of record, so
#	an index is created on shape_id
#
import csv
import MySQLdb
import sys
import string
import os

def import_shapes(dbhost, dbuser, dbpass, dbname, filename, action):
	if action=="-append":
		print "Appending %s into %s.shapes" %(filename,dbname)
	else:
		print "Converting %s into %s.shapes" %(filename,dbname)
	
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
			print "   [*] Dropping table shapes, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS shapes")
			cursor.execute ("""CREATE TABLE shapes (
							shape_id CHAR(32),
							shape_pt_lat DOUBLE,
							shape_pt_lon DOUBLE,
							shape_pt_sequence INTEGER,
							INDEX shape_id USING HASH (shape_id)
							)
						""")
			print "   [*] Table shapes dropped, and a new one created."
			
		
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
			
			print "   [*] Adding records into %s.shapes " % dbname
			addLines = 0
			for rowvalues in reader:
				shape_id = rowvalues['shape_id']
				shape_pt_lat = rowvalues['shape_pt_lat']
				shape_pt_lon = rowvalues['shape_pt_lon']
				shape_pt_sequence = rowvalues['shape_pt_sequence']
				cursor.execute("""
							INSERT INTO shapes (shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence)
							VALUES
							(%s, %s, %s, %s)
							""", (shape_id,shape_pt_lat,shape_pt_lon,shape_pt_sequence))
				addLines = addLines + 1
			cvsfile.close()
					
			#check
			print "   [*] Number of lines read from ", filename, ": %d" %addLines	 
			
		print "   [*] Checking imported %s.shapes" % dbname
		cursor.execute("SELECT COUNT(*) FROM shapes")	 
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
	import_shapes(dbhost, dbuser, dbpass, dbname, filename, "-refresh")
	
def append(dbhost, dbuser, dbpass, dbname, filename):
	import_shapes(dbhost, dbuser, dbpass, dbname, filename, "-append")
