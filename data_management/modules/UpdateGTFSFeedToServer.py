#! /usr/bin/python

import sys, getopt, os
from gtfs import server

def usage():
	print 'Usage:'
	print '\t %s  [options] <GTFS feed dir>' % (os.path.basename(sys.argv[0]))
	print 'Options:'
	print '\t --help        This information'
	print '\t -h --host=    Host where the database resides'
	print '\t -u --user=    Username used to connect to database'
	print '\t -p --passwd=  Password used to connect to database'
	print '\t -d --dbname=  Name of the database'
	print ''

try:                                
	opts, args = getopt.getopt(sys.argv[1:], "h:u:p:d:", ["help", "host=", "user=", "passwd=", "dbname="])
except getopt.GetoptError:
	print "Parameter parsing error"
	usage()
	sys.exit(1)

serverHostName = ""
serverUserName = ""
serverDbPasswd = ""
serverDbName = ""
#print "args: ", args
#print "opts: ", opts
for opt, arg in opts:
	if opt in ("--help"):
		usage()
		sys.exit(1)
	elif opt in ("-h", "--host"):
		serverHostName = arg
	elif opt in ("-u", "--user"):
		serverUserName = arg
	elif opt in ("-p", "--passwd"):
		serverDbPasswd = arg
	elif opt in ("-d", "--dbname"):
		serverDbName = arg
        else:
		print "Parameter error!"
		usage()
		sys.exit(1)

if (serverHostName=="") or (serverUserName=="") or (serverDbName==""):
	print "\n[*] Fatal: some parameters are empty"
	print "serverHostName = ", serverHostName 
	print "serverUserName = ", serverUserName 
	print "serverDbName =   ", serverDbName 
	usage()
	sys.exit(1) 

feedName = args[0]
if not os.path.exists(feedName):
	print "Error: Path %s does not exist!!!" % feedName
	sys.exit(1) 

server.renew_gtfs_feed(serverHostName, serverUserName, serverDbPasswd, serverDbName, feedName);

