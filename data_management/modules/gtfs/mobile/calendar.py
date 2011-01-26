#!/usr/bin/python
#
#  import_calendar.py
#  
#
#  Created by Zhenwang Yao on 03/11/08.
#  Copyright (c) 2008 Music Motion. All rights reserved.
#

## This module import calendar.txt to table 'calendar' in a sqlite database
# 
# It take two parameters, as
#	   import_calendar $dbName $cvsFile
#
# Thus, it imports $cvsFile (calendar.txt) to $dbName.calendar.
#	   if $dbName.calendar exists, it deletes the table first.
#
# $dbName.calendar table structure: 
#      service_id CHAR(64) PRIMARY KEY,                        
#      monday INT,
#      tuesday INT,
#      wednesday INT,
#      thursday INT,
#      friday INT,
#      saturday INT,
#      sunday INT,
#      start_date CHAR(32),
#      end_date CHAR(32)                        
#
import csv
import sqlite3
import sys
import string
import os

def import_calendar(dbname, filename, action):
	if action=="-append":
		print "Appending %s into %s.calendar" %(filename,dbname)
	else:
		print "Converting %s into %s.calendar" %(filename,dbname)
	
	try:
		#create table
		print "   [*] Connecting to database %s." %dbname
		conn = sqlite3.connect(dbname, isolation_level=None)
		cursor = conn.cursor()
		print "   [*] Connected to database."

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
					INSERT OR REPLACE INTO calendar (service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date)
					VALUES
					(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
					""", (rowvalues['service_id'].strip(),rowvalues['monday'],rowvalues['tuesday'],rowvalues['wednesday'],rowvalues['thursday'],rowvalues['friday'],rowvalues['saturday'],rowvalues['sunday'],rowvalues['start_date'],rowvalues['end_date']) )
				else:
					cursor.execute("""
					INSERT INTO calendar (service_id,monday,tuesday,wednesday,thursday,friday,saturday,sunday,start_date,end_date)
					VALUES
					(?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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

	except Exception, err:
		print "Error occured during importing (at Line %d), with error: %s!!" %(addLines, str(err))
		print ""
		#sys.exit(1) 	

	conn.close()
def refresh(dbname, filename):
	import_calendar(dbname, filename, "-refresh")
	
def append(dbname, filename):
	import_calendar(dbname, filename, "-append")
