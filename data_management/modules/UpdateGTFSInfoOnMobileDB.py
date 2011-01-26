#! /usr/bin/python

import sys, getopt, os
from gtfs import mobile

def usage():
	print 'Usage:'
	print '\t %s  [options] <Sqlite dbName> <GTFS info file>' % (os.path.basename(sys.argv[0]))
	print 'Options:'
	print '\t --help        This information'
	print '\t -v --version= The version of the database'
	print ''

try:                                
	opts, args = getopt.getopt(sys.argv[1:], "v:", ["help", "version="])
except getopt.GetoptError:
	print "Parameter parsing error"
	usage()
	sys.exit(1)

dbName = args[0]
fileName = args[1]
dbVersion = ""
#print "args: ", args
#print "opts: ", opts
for opt, arg in opts:
	if opt in ("--help"):
		usage()
		sys.exit(1)
	elif opt in ("-v", "--version"):
		dbVersion = arg
        else:
		print "Parameter error!"
		usage()
		sys.exit(1)

if (dbVersion=="") or (dbName=="") or (fileName==""):
	print "\n[*] Fatal: some parameters are empty"
	print "[*]       dbVersion = ", dbVersion 
	print "[*]       dbName    = ", dbName 
	print "[*]       fileName  = ", fileName 
	usage()
	sys.exit(1) 

if not os.path.exists(fileName):
	print "Error: Path %s does not exist!!!" % fileName
	sys.exit(1) 

mobile.update_gtfs_info(dbName, fileName, dbVersion);

