#!/usr/bin/python
#
#  extract_route_stops.py
#  
#  Created by Zhenwang Yao on 03/11/08.
#  Copyright (c) 2008 Music Motion. All rights reserved.
#
## This module extract unique set of (route_id, stop_id, direction_id) from mySQL server,
#        and extract them into the route_stops table of a sqlite database
# 
# It take two parameters, as
#	   import_stops $sqliteDBName $mySQLDbName
#
# Thus, it extract (route_id, stop_id, direction_id) from $mySQLDbName to $sqliteDBName.route_stops.
#
# $dbName.route_stops table structure: 
#      route_id CHAR(16),
#      stop_id CHAR(32),
#      direction_id CHAR(16) 
#
import csv
import sqlite3
import MySQLdb
import sys
import string
import os

def extract_route_stops(dbname, mysqldb):
	print "   Extract (route, stop, direction) in %s into %s.route_stops" %(mysqldb,dbname)

	try:
		#create sqlite table
		print "   [*] Connecting to sqlite database %s." %dbname
		sqliteconn = sqlite3.connect(dbname, isolation_level=None)
		sqlitecursor = sqliteconn.cursor()
		print "   [*] Connected to sqlite database."

		print "   [*] Dropping sqlite table route_stops, and creating a new one."
		sqlitecursor.execute ("DROP TABLE IF EXISTS route_stops")
		sqlitecursor.execute ("""CREATE TABLE route_stops (
						route_id CHAR(16),
						stop_id CHAR(32),
						direction_id CHAR(16)
						)
				""")	
		
		print "   [*] Create stop_index ON route_stops"		
		sqlitecursor.execute ("CREATE INDEX stop_index ON route_stops(stop_id)")
		print "   [*] Create route_index ON route_stops"		
		sqlitecursor.execute ("CREATE INDEX route_index ON route_stops(route_id)")
		print "   [*] Table route_stops dropped, and a new one created."
	except:
		print "Error occured during creating sqlite3 table %d" %dbname
		sys.exit(1) 


	try:	
		#connect to the mySQL database
		print "   [*] Connecting to mySQL database %s." %mysqldb
		mysqlconn = MySQLdb.connect(host = "localhost",
							   user = "root",
							   passwd = "awang",
							   db = mysqldb) 	   
		print "   [*] Connected to mySQL database."
	
	except MySQLdb.Error, e:
		print "Error %d %s" % (e.args[0], e.args[1])
		sys.exit(1) 	


	try:
		mysqlcursor = mysqlconn.cursor()
		print "   [*] Extracting unique (route_id, stop_id, direction_id)."
		mysqlcursor.execute ("""SELECT DISTINCT stops.stop_id, trips.route_id, trips.direction_id
					FROM stops, stop_times, trips
					WHERE stops.stop_id=stop_times.stop_id AND
					trips.trip_id=stop_times.trip_id
					""")

		# Fetch all the rows in a list of lists, and insert to sqlite db
		results = mysqlcursor.fetchall()
		addLines = 0
		for rowvalues in results:
			stop_id = rowvalues[0]
			route_id = rowvalues[1]
			direction_id = rowvalues[2]

			sqlitecursor.execute("""
					INSERT INTO route_stops (route_id,stop_id,direction_id)
					VALUES
					(?, ?, ?)
					""", (route_id,stop_id,direction_id)  )

			addLines = addLines + 1

		#check
		print "   [*] Number of records read from ", mysqldb, ": %d" %addLines	 
		print "   [*] Checking imported %s.route_sotps" % dbname
		sqlitecursor.execute("SELECT COUNT(*) FROM route_stops")	 
		print "   [*] Number of row in the table: ", sqlitecursor.fetchone()[0]
		print "   [*] Done \n"	  
	
		#close down
		mysqlconn.close()
		sqliteconn.close()

	except MySQLdb.Error, e:
		print "Error %d %s" % (e.args[0], e.args[1])
		sys.exit(1) 	   

def generate(dbname, mysqldb):
	extract_route_stops(dbname, mysqldb)
	

