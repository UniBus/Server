#! /usr/bin/python
import calendar
import calendar_dates
import routes
import stops
import stop_times
import route_stops
import trips
import dbinfo
import gtfs_info
import favorite
import sys
import string
import os

def import_to_offline_db(dbname, feeddir, action, version):
	print "\nUniBus-SQLite-Tool Suite"
	print "Covert GTFS data from csv format to sqlite format."
	print "Copyright @ Zhenwang.Yao 2008. \n"
	
	if not os.path.exists(feeddir):
		print "Error: Path %s does not exist!!!" % feeddir
		sys.exit(1) 
	
	if action == "-append":
		calendar.append(dbname, os.path.join(feeddir, "calendar.txt"))
		calendar_dates.append(dbname, os.path.join(feeddir, "calendar_dates.txt"))
		stop_times.append(dbname, os.path.join(feeddir, "stop_times.txt"))
		trips.append(dbname, os.path.join(feeddir, "trips.txt"))
		dbinfo.add(dbname, version)

	else: #action == "-refresh"
		#citydb.drop(dbname)
		calendar.refresh(dbname, os.path.join(feeddir, "calendar.txt"))
		calendar_dates.refresh(dbname, os.path.join(feeddir, "calendar_dates.txt"))
		stop_times.refresh(dbname, os.path.join(feeddir, "stop_times.txt"))
		trips.refresh(dbname, os.path.join(feeddir, "trips.txt"))
		dbinfo.add(dbname, version)

def import_to_city_db(dbname, feeddir, action, version):
	print "\nUniBus-SQLite-Tool Suite [For offline browsing]"
	print "Covert GTFS data from csv format to sqlite format."
	print "Copyright @ Zhenwang.Yao 2008. \n"	
	
	if not os.path.exists(feeddir):
		print "Error: Path %s does not exist!!!" % feeddir
		sys.exit(1) 
	
	if action == "-append":
		routes.append(dbname, os.path.join(feeddir, "routes.txt"))
		stops.append(dbname, os.path.join(feeddir, "stops.txt"))
		dbinfo.add(dbname, version)
		favorite.add(dbname)
		favorite.add_v13(dbname)

	else: #action == "-refresh"
		#citydb.drop(dbname)
		routes.refresh(dbname, os.path.join(feeddir, "routes.txt"))
		stops.refresh(dbname, os.path.join(feeddir, "stops.txt"))
		dbinfo.add(dbname, version)
		favorite.add(dbname)
		favorite.add_v13(dbname)

def update_city_db(dbname, feeddir, version):
	import_to_city_db(dbname, feeddir, "-refresh", version)
	
def append_city_db(dbname, feeddir, version):
	import_to_city_db(dbname, feeddir, "-append", version)

def update_offline_db(dbname, feeddir, version):
	import_to_offline_db(dbname, feeddir, "-refresh", version)
	
def append_offline_db(dbname, feeddir, version):
	import_to_offline_db(dbname, feeddir, "-append", version)

def generate_route_stops_in_city_db(dbname, mysqldbname):
	route_stops.generate(dbname, mysqldbname)

def update_gtfs_info(dbname, filename, version):
	gtfs_info.update(dbname, filename)
	dbinfo.add(dbname, version)
