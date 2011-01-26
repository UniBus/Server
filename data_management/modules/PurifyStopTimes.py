#! /usr/bin/python

import csv, time, string, math
import sys, getopt, os, shutil
from gtfs import server

def usage():
	print 'Usage:'
	print '\t %s  [options] <GTFS feed dir>' % (os.path.basename(sys.argv[0]))
	print 'Options:'
	print '\t --help        This information'
	print ''


def get_all_frequency(filename):
	#try:
	#insert record
	#trip_id,start_time,end_time,headway_secs,exact_times
	frequencies = {}
	print "   [*] Opening file %s " % filename
	cvsfile = open(filename)
	headerreader = csv.reader(cvsfile,skipinitialspace=True)
	fieldnames = headerreader.next()
	reader = csv.DictReader(cvsfile, fieldnames, restkey='unknown', restval='',skipinitialspace=True)
	#print fieldnames

	addLines = 0
	currentLine = 1
	for rowvalues in reader:
		currentLine = currentLine + 1
		trip_id = rowvalues['trip_id'] #.strip()
		start_time = rowvalues['start_time'] #.strip(), will slow down a lot
		end_time = rowvalues['end_time']
		headway_secs = rowvalues['headway_secs']

		if not frequencies.has_key(trip_id):
			frequencies[trip_id] = []
		#else:
		#	print "   [*] Warning: Repeated trip_id (%s) in frequencies.txt" % trip_id
		
		theFrequency = {"trip_id":trip_id, "start_time":start_time, "end_time":end_time, "headway_secs":headway_secs}
		frequencies[trip_id].append( theFrequency )

		addLines = addLines + 1
	
	#check
	print "   [*] Number of lines read from ", filename, ": %d" %addLines	

	#close down
	cvsfile.close()

	#except:
	#	print "Error occured during importing!!"
	#	sys.exit(1) 	

	return frequencies

#
# stops is organized as dictionary
#	{
#		[trip_id]: 
#			{
#				[stop_seq]: {stop_id, arrival_time, departure_time, ...}
#			}
#
#		[trip_id]: 
#			{
#				....
#			}
#
#       }
def get_all_stop_times(filename):
	#try:
	#insert record
	stops = {}
	print "   [*] Opening file %s " % filename
	cvsfile = open(filename)
	headerreader = csv.reader(cvsfile,skipinitialspace=True)
	fieldnames = headerreader.next()
	reader = csv.DictReader(cvsfile, fieldnames, restkey='unknown', restval='',skipinitialspace=True)
	#print fieldnames

	addLines = 0
	currentLine = 1
	for rowvalues in reader:
		currentLine = currentLine + 1
		stop_id = rowvalues['stop_id'].replace(' ', '') #.strip(), will slow down a lot
		trip_id = rowvalues['trip_id'] #.strip()
		if not stops.has_key(trip_id):
			stops[trip_id] = {}
		stopsInTrip = stops[trip_id]

		stop_sequence = rowvalues['stop_sequence']
		arrival_time_str = string.strip(rowvalues['arrival_time'])
		departure_time_str = string.strip(rowvalues['departure_time'])
	
		arrival_time = arrival_time_str.rjust(8, '0')
		departure_time = departure_time_str.rjust(8, '0')
		if arrival_time == "00000000":
			print "   [*] WARNING: Invalid arrival times around line ", currentLine
			continue

		try:
			stop_headsign = rowvalues['stop_headsign']
		except:
			stop_headsign = ''
		
		theStop = {"stop_id":stop_id, "arrival_time":arrival_time_str, "departure_time":departure_time_str, "stop_headsign":stop_headsign}
		stopsInTrip[stop_sequence] = theStop

		addLines = addLines + 1
	
	#check
	print "   [*] Number of lines read from ", filename, ": %d" %addLines	

	#close down
	cvsfile.close()

	#except:
	#	print "Error occured during importing!!"
	#	sys.exit(1) 	

	return stops

#
# trips is organized as dictionary
#	{[trip_id]: {route_id, service_id, trip_id, ....}}
def get_all_trips(filename):
	#try:
	#insert record
	trips = {}
	print "   [*] Opening file %s " % filename
	cvsfile = open(filename)
	headerreader = csv.reader(cvsfile,skipinitialspace=True)
	fieldnames = headerreader.next()
	reader = csv.DictReader(cvsfile, fieldnames, restkey='unknown', restval='',skipinitialspace=True)
	#print fieldnames

	addLines = 0
	currentLine = 1
	for rowvalues in reader:
		currentLine = currentLine + 1
		route_id = rowvalues['route_id'] #.strip(), will slow down a lot
		service_id = rowvalues['service_id']
		trip_id = rowvalues['trip_id']

		trip_headsign = rowvalues['trip_headsign']
		direction_id = rowvalues['direction_id']
		block_id = rowvalues['block_id']
		shape_id = rowvalues['shape_id']

		the_trip = {"route_id":route_id, "service_id":service_id, "trip_id":trip_id, "trip_headsign":trip_headsign, "direction_id":direction_id, "block_id":block_id, "shape_id":shape_id}
		trips[trip_id] = the_trip

		addLines = addLines + 1
	
	#check
	print "   [*] Number of lines read from ", filename, ": %d" %addLines	

	#close down
	cvsfile.close()

	#except:
	#	print "Error occured during importing!!"
	#	sys.exit(1) 	

	return trips


def GetTimeHMS(t):
	hms_str = string.split(t, ':')
	hms = [string.atoi(hms_str[0]), string.atoi(hms_str[1]), string.atoi(hms_str[2])]
	return hms


def GetSecondInHMS(t):
	return (t[0]*3600 + t[1] * 60 + t[2])


def GetHMSTimeWithOffset(start, offsetInSec):
	#strt: [h, m, s]
	h = start[0]
	m = start[1]
	s = start[2]

	s += offsetInSec
	m += math.floor(s/60)
	s = s % 60
	h += math.floor(m/60)
	m = m % 60
	
	return [h, m, s]


def GetTimeWithOffset(start, offsetInSec):
	hms = GetTimeHMS(start)
	hms = GetHMSTimeWithOffset(hms, offsetInSec)
	return "%02d:%02d:%02d"%(hms[0], hms[1], hms[2])
	


def GetNumberOfIntervals(start, end, interval):
	#       start: 6:45:00
	#         end: 7:44:00
	#headway_secs: 3600
	start_hms = GetTimeHMS(start)
	start_sec = GetSecondInHMS(start_hms)
	end_hms = GetTimeHMS(end)
	end_sec = GetSecondInHMS(end_hms)

	delta_sec = end_sec - start_sec
	interval_sec = interval
	return math.ceil(delta_sec/interval_sec)


def GetTimeDifference(start, end):
	#       start: 6:45:00
	#         end: 7:44:00
	#headway_secs: 3600
	start_hms = GetTimeHMS(start)
	start_sec = GetSecondInHMS(start_hms)
	end_hms = GetTimeHMS(end)
	end_sec = GetSecondInHMS(end_hms)

	return ( end_sec - start_sec )


#
# Adjusted stop time is organized as dictionary
#	{
#		[new_trip_id]: 
#			[
#				{stop_id_1, arrival_time, departure_time, ...}
#				{stop_id_2, arrival_time, departure_time, ...}
#			]
#	}
#
def AdjustStopTimesByFrequency(stopsInTrip, frequencies):
	new_stop_times = {}
	
	trip_count = 0
	for frequency in frequencies:
		trip_id = frequency["trip_id"]
		start_time = frequency["start_time"]
		end_time = frequency["end_time"]
		headway_secs = string.atoi(frequency["headway_secs"])

		#print stopsInTrip
		num_of_intervals = GetNumberOfIntervals(start_time, end_time, headway_secs)
		for interval in range(int(num_of_intervals)):
			new_stops_in_trip = []
			trip_count += 1
			new_trip_id = "%s_%d"%(trip_id, trip_count)
			new_stop_times[new_trip_id] = new_stops_in_trip
			for stop_seq in sorted(stopsInTrip.keys()):
				stop = stopsInTrip[stop_seq]
				if stop_seq == '1':
					based_time_arr = stop["arrival_time"]
					based_time_dep = stop["arrival_time"]
				time_difference_arr = GetTimeDifference(based_time_arr, stop["arrival_time"])
				time_difference_dep = GetTimeDifference(based_time_dep, stop["departure_time"])
				new_stop = {}
				new_stop["stop_id"] = stop["stop_id"]
				new_stop["arrival_time"] = GetTimeWithOffset(start_time, time_difference_arr + interval * headway_secs)
				new_stop["departure_time"] = GetTimeWithOffset(start_time, time_difference_dep + interval * headway_secs)
				new_stop["stop_headsign"] = stop["stop_headsign"]
				new_stops_in_trip.append(new_stop)
			
	return new_stop_times


try:                                
	opts, args = getopt.getopt(sys.argv[1:], "h:", ["help"])
except getopt.GetoptError:
	print "Parameter parsing error"
	usage()
	sys.exit(1)

#print "args: ", args
#print "opts: ", opts
for opt, arg in opts:
	if opt in ("-h", "--help"):
		usage()
		sys.exit(1)
        else:
		print "Parameter error!"
		usage()
		sys.exit(1)


if len(args) == 0:
	usage()
	sys.exit(1)

gtfsFeedDir = args[0]
gtfsFeedStopTimes = os.path.join(gtfsFeedDir, "stop_times.txt")
gtfsFeedStopTimesBackup = os.path.join(gtfsFeedDir, "stop_times_original.txt")
gtfsFeedTrips = os.path.join(gtfsFeedDir, "trips.txt")
gtfsFeedTripsBackup = os.path.join(gtfsFeedDir, "trips_original.txt")
gtfsFeedFrequency = os.path.join(gtfsFeedDir, "frequencies.txt")
if not os.path.exists(gtfsFeedFrequency):
	print "   [*] Done: Frequency file %s does not exist!!!" % gtfsFeedFrequency
	sys.exit(1) 

frequencies = get_all_frequency(gtfsFeedFrequency)
if len(frequencies) == 0:
	print "   [*] Done: Frequency file is empty !!!"
	sys.exit(1)

#copy orginal file to backup
if not os.path.exists(gtfsFeedStopTimesBackup):
	shutil.copy(gtfsFeedStopTimes, gtfsFeedStopTimesBackup)	
if not os.path.exists(gtfsFeedTripsBackup):
	shutil.copy(gtfsFeedTrips, gtfsFeedTripsBackup)	

stops = get_all_stop_times(gtfsFeedStopTimesBackup)
trips = get_all_trips(gtfsFeedTripsBackup)

output = open(gtfsFeedStopTimes, "w")
output.write("trip_id, stop_id, arrival_time, departure_time, stop_headsign\n")

output2 = open(gtfsFeedTrips, "w")
output2.write("route_id, service_id, trip_id, trip_headsign, direction_id, block_id, shape_id\n")

for trip_id in stops.keys():
	theStopsInTrip = stops[trip_id]
	if not frequencies.has_key(trip_id):
		#print "   [*] Warning: trip_id: %s doesn't exist in the frequency file?!" % trip_id
		newStopsInTrip = {}
		newStops = []
		for stop_seq in sorted(theStopsInTrip.keys()):
			newStops.append(theStopsInTrip[stop_seq])
		newStopsInTrip[trip_id] = newStops
	else:		
		theFrequency = frequencies[trip_id]
		newStopsInTrip = AdjustStopTimesByFrequency(theStopsInTrip, theFrequency)

	#print newStopsInTrip
	for new_trip_id in newStopsInTrip:
		stops_in_trip = newStopsInTrip[new_trip_id]
		#route_id, service_id, trip_id, trip_headsign, direction_id, block_id, shape_id
		trip_org = trips[trip_id]
		output2.write("%s, %s, %s, %s, %s, %s, %s\n" % (trip_org["route_id"], trip_org["service_id"], new_trip_id, trip_org["trip_headsign"], trip_org["direction_id"], trip_org["block_id"], trip_org["shape_id"] ))
		for aStop in stops_in_trip:
			stop_id = aStop["stop_id"]
			arrival_time = aStop["arrival_time"]
			departure_time = aStop["departure_time"]
			stop_headsign = aStop["stop_headsign"]	
			output.write("%s, %s, %s, %s, %s\n"%(new_trip_id, stop_id, arrival_time, departure_time, stop_headsign))

output2.close()		
output.close()		


