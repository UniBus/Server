#!/usr/bin/python
#
#  add_favorites.py
#
#  Created by Zhenwang Yao on 03/11/08.
#  Copyright (c) 2008 Music Motion. All rights reserved.
#

## This module add a 'favorites' table in a city database.
# 
# It take two parameters, as
#      add_favorites $dbName
#
# Thus, it creates an empty favorite table into the database.
#
# favorites table structure: 
#      stop_id CHAR(16),
#      route_id CHAR(32),
#      route_name CHAR(32),
#      bus_sign CHAR(128)",
#      direction_id CHAR(4)
#
import csv
import sqlite3
import sys
import string
import os

def add(dbname):
	print "   Adding db-information into ", dbname

	try:
		#create table
		print "   [*] Connecting to database %s." %dbname
		conn = sqlite3.connect(dbname, isolation_level=None)
		cursor = conn.cursor()
		print "   [*] Connected to database."

		print "   [*] Dropping table favorites, and creating a new one."
		cursor.execute ("DROP TABLE IF EXISTS favorites")
		cursor.execute ("""CREATE TABLE IF NOT EXISTS favorites (
						stop_id CHAR(16),
						route_id CHAR(32),
						route_name CHAR(32),
						direction_id CHAR(4),
						bus_sign CHAR(128)
						)
						""")		
		print "   [*] Table favorites dropped, and a new one created."
	
		#insert record
		print "   [*] Checking %s.favorites" % dbname
		cursor.execute("SELECT COUNT(*) FROM favorites")
		print "   [*] Number of row in the table: ", cursor.fetchone()[0]	
		print "   [*] Done \n"

		#close down
		cursor.close()

	except:
		print "Error occured during importing!!"
		sys.exit(1)		

	conn.commit()
	conn.close()

def add_v13(dbname):
	print "   Adding db-information into ", dbname

	try:
		#create table
		print "   [*] Connecting to database %s." %dbname
		conn = sqlite3.connect(dbname, isolation_level=None)
		cursor = conn.cursor()
		print "   [*] Connected to database."

		print "   [*] Dropping table favorites2, and creating a new one."
		cursor.execute ("DROP TABLE IF EXISTS favorites2")
		cursor.execute ("""CREATE TABLE IF NOT EXISTS favorites2 (
						stop_id CHAR(16),
						route_id CHAR(32),
						route_name CHAR(32),
						direction_id CHAR(4),
						bus_sign CHAR(128),
						rowindex DOUBLE
						)
						""")		
		print "   [*] Table favorites2 dropped, and a new one created."
	
		#insert record
		print "   [*] Checking %s.favorites2" % dbname
		cursor.execute("SELECT COUNT(*) FROM favorites2")
		print "   [*] Number of row in the table: ", cursor.fetchone()[0]	
		print "   [*] Done \n"

		#close down
		cursor.close()

	except Exception, err:
		print "Error occured during importing, with error: %s!!" %str(err)
		sys.exit(1)		

	conn.commit()
	conn.close()

def add_tag_db(dbname):
	print "   Adding db-information into ", dbname

	try:
		#create table
		print "   [*] Connecting to database %s." %dbname
		conn = sqlite3.connect(dbname, isolation_level=None)
		cursor = conn.cursor()
		print "   [*] Connected to database."

		print "   [*] Dropping table tags, and creating a new one."
		cursor.execute ("DROP TABLE IF EXISTS tags")
		cursor.execute ("""CREATE TABLE IF NOT EXISTS tags (
						tag_id INTEGER PRIMARY KEY,
						tag_name CHAR(32)
						)
						""")		
		print "   [*] Table tags dropped, and a new one created."
		print "   [*] Insert the record into %s.dbinfo " % dbname	
		cursor.execute("INSERT INTO dbinfo (tag_name) VALUES ('To Work')")
		cursor.execute("INSERT INTO dbinfo (tag_name) VALUES ('Go Home')")
	
		print "   [*] Dropping table taggeds, and creating a new one."
		cursor.execute ("DROP TABLE IF EXISTS taggeds")
		cursor.execute ("""CREATE TABLE IF NOT EXISTS taggeds (
						stop_id CHAR(16),
						route_id CHAR(32),
						route_name CHAR(32),
						direction_id CHAR(4),
						bus_sign CHAR(128),
						tag_id,
						)
						""")		
		print "   [*] Table taggeds dropped, and a new one created."
	
		#insert record
		print "   [*] Checking %s.tags" % dbname
		cursor.execute("SELECT COUNT(*) FROM tags")
		print "   [*] Number of row in the table: ", cursor.fetchone()[0]	
		print "   [*] Checking %s.taggeds" % dbname
		cursor.execute("SELECT COUNT(*) FROM taggeds")
		print "   [*] Number of row in the table: ", cursor.fetchone()[0]	
		print "   [*] Done \n"

		#close down
		cursor.close()

	except:
		print "Error occured during importing!!"
		sys.exit(1)		

	conn.commit()
	conn.close()
