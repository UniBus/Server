#!/usr/bin/python
#
#  import_calendar_dates.py
#  
#
#  Created by Zhenwang Yao on 03/11/08.
#  Copyright (c) 2008 Music Motion. All rights reserved.
#

## This module import calendar_dates.txt to table 'calendar_dates' in a sqlite database
# 
# It take two parameters, as
#	   import_calendar_dates $dbName $cvsFile
#
# Thus, it imports $cvsFile (calendar_dates.txt) to $dbName.calendar_dates.
#	   if $dbName.calendar_dates exists, it deletes the table first.
#
# $dbName.calendar_dates table structure: 
#	   service_id CHAR(64),
#	   date CHAR(32),
#	   exception_type CHAR(8)
#
import csv
import sqlite3
import sys
import string
import os

def import_calendar_dates(dbname, filename, action):
	if action=="-append":
		print "   Appending %s into %s.calendar_dates" %(filename,dbname)
	elif action=="-refresh":
		print "   Converting %s into %s.calendar_dates" %(filename,dbname)
	else:
		print "   Wrong action[%s] argument!" %action
		sys.exit(1)

	try:
		#create table
		print "   [*] Connecting to database %s." %dbname
		conn = sqlite3.connect(dbname, isolation_level=None)
		cursor = conn.cursor()
		print "   [*] Connected to database."

		if action == "-refresh":
			print "   [*] Dropping table calendar_dates, and creating a new one."
			cursor.execute ("DROP TABLE IF EXISTS calendar_dates")
			cursor.execute ("""CREATE TABLE calendar_dates (
							service_id CHAR(64),
							date CHAR(32),
							exception_type CHAR(8)
							)
						""")

		#insert record
		if not os.path.exists(filename):
			print "   [*] WARNING: %s does not exist.\n" %filename
		else:
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
				if action == "-update":
					cursor.execute("""
							INSERT OR REPLACE INTO calendar_dates (service_id,date,exception_type)
							VALUES
							(?, ?, ?)
							""", (service_id,date,exception_type) )
				else:
					cursor.execute("""
							INSERT INTO calendar_dates (service_id,date,exception_type)
							VALUES
							(?, ?, ?)
							""", (service_id,date,exception_type) )
				addLines = addLines + 1
		
			#check
			print "   [*] Number of lines read from ", filename, ": %d" %addLines	
			print "   [*] Checking imported %s.calendar_dates" % dbname
			cursor.execute("SELECT COUNT(*) FROM calendar_dates")
			print "   [*] Number of row in the table: ", cursor.fetchone()[0]
			print "   [*] Done \n"

			cvsfile.close()

		#close down
		cursor.close()

	except Exception, err:
		print "Error occured during importing (at Line %d), with error: %s!!" %(addLines, str(err))
		print ""
		#sys.exit(1) 	

	conn.close()

def refresh(dbname, filename):
	import_calendar_dates(dbname, filename, "-refresh")
	
def append(dbname, filename):
	import_calendar_dates(dbname, filename, "-append")
