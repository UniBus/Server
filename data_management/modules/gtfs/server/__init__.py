#! /usr/bin/python
import agency
import calendar
import calendar_dates
import citydb
import routes
import shapes
import stops
import stop_times
import trips
import gtfs_info
import sys
import string
import os

def import_gtfs_feed(dbhost, dbuser, dbpass, dbname, feeddir, action):
	print "\nUniBus-MySQL-Tool Suite"
	print "Import GTFS data from csv format to MySQL database."
	print "Copyright @ Zhenwang.Yao 2008. \n"
	
	if not os.path.exists(feeddir):
		print "Error: Path %s does not exist!!!" % feeddir
		sys.exit(1) 
	
	if action == "-append":
		agency.append(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "agency.txt"))
		calendar.append(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "calendar.txt"))
		calendar_dates.append(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "calendar_dates.txt"))
		routes.append(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "routes.txt"))
		shapes.append(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "shapes.txt"))
		stops.append(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "stops.txt"))
		stop_times.append(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "stop_times.txt"))
		trips.append(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "trips.txt"))

	else: #action == "-refresh"
		#citydb.drop(dbname)
		citydb.create(dbhost, dbuser, dbpass, dbname)
		agency.refresh(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "agency.txt"))
		calendar.refresh(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "calendar.txt"))
		calendar_dates.refresh(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "calendar_dates.txt"))
		routes.refresh(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "routes.txt"))
		shapes.refresh(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "shapes.txt"))
		stops.refresh(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "stops.txt"))
		stop_times.refresh(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "stop_times.txt"))
		trips.refresh(dbhost, dbuser, dbpass, dbname, os.path.join(feeddir, "trips.txt"))

def renew_gtfs_feed(dbhost, dbuser, dbpass, dbname, feeddir):
	import_gtfs_feed(dbhost, dbuser, dbpass, dbname, feeddir, "-refresh")
	
def append_gtfs_feed(dbhost, dbuser, dbpass, dbname, feeddir):
	import_gtfs_feed(dbhost, dbuser, dbpass, dbname, feeddir, "-append")
	
def import_gtfs_info(dbhost, dbuser, dbpass, dbname, filename):
	gtfs_info.generate(dbhost, dbuser, dbpass, dbname, filename)

