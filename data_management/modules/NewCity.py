#! /usr/bin/python

import sys, getopt, os
from html import city

def usage():
	print 'Usage:'
	print '\t %s  [options] <cityId> <cityDirectory>' % (os.path.basename(sys.argv[0]))
	print 'Options:'
	print '\t --help        This information'
	print ''

try:                                
	opts, args = getopt.getopt(sys.argv[1:], "v:", ["help", "version="])
except getopt.GetoptError:
	print "Parameter parsing error"
	usage()
	sys.exit(1)

cityId = args[0]
cityDir = args[1]
#print "args: ", args
#print "opts: ", opts
for opt, arg in opts:
	if opt in ("--help"):
		usage()
		sys.exit(1)
        else:
		print "Parameter error!"
		usage()
		sys.exit(1)

if not os.path.exists(cityDir):

	confirm = raw_input('Directory %s does not exist, do you want to create one![yes/no]?'%cityDir)
	confirm	= confirm.lower()
	while (confirm != 'yes') and (confirm != 'no') :
		confirm = raw_input('Directory %s does not exist, do you want to create one![yes/no]?'%cityDir)
		confirm	= confirm.lower()

	if confirm == 'yes':
		try:
			os.mkdir(cityDir)
		except:
			print "Failed to create path: " % cityDir
			sys.exit(1) 
	else:
		sys.exit(0)

city.create(cityId, cityDir)

