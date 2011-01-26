#!/usr/bin/python
#
#  add_dbinfo.py
#  
#
#  Created by Zhenwang Yao on 03/11/08.
#  Copyright (c) 2008 Music Motion. All rights reserved.
#

## This module updates 'dbinfo' table in a sqlite database.
# 
# It take two parameters, as
#      add_dbinfo $dbName
#
# Thus, it adds a dbinfo table into the database.
#      if dbinfo exists, it deletes the table first.
#      After that, some actual record may be added.
#
# dbinfo table structure: 
#      parameter CHAR(32),
#      value CHAR(32)
#
import csv
import sqlite3
import sys
import string
import os

def add(dbname, version):
	print "   Adding db-information into ", dbname

	try:
		#create table
		print "   [*] Connecting to database %s." %dbname
		conn = sqlite3.connect(dbname, isolation_level=None)
		cursor = conn.cursor()
		print "   [*] Connected to database."

		print "   [*] Dropping table dbinfo, and creating a new one."
		cursor.execute ("DROP TABLE IF EXISTS dbinfo")
		cursor.execute ("""CREATE TABLE IF NOT EXISTS dbinfo (
						parameter CHAR(32),
						value CHAR(32)
						)
						""")		
		print "   [*] Table dbinfo dropped, and a new one created."
	
		#insert record
		print "   [*] Insert the record into %s.dbinfo " % dbname	
		cursor.execute("INSERT INTO dbinfo (parameter, value) VALUES (?,?)", ('db_version', version))
	
		#check
		print "   [*] Checking imported %s.dbinfo" % dbname
		cursor.execute("SELECT COUNT(*) FROM dbinfo")
		print "   [*] Number of row in the table: ", cursor.fetchone()[0], " and they are as follows:"	
		cursor.execute("SELECT * FROM dbinfo")
		for row in cursor.fetchall():
			print "          ", row	
		print "   [*] Done \n"

		#close down
		cursor.close()

	except Exception, err:
		print "Error occured during importing, with error: %s!!" %str(err)
		sys.exit(1)		

	conn.commit()
	conn.close()
