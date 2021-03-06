<?php
//=============================================================================
/// The code in this file queries whole day schedule, given a stop.
//
//  This file is designed to used as part of the quering script, 
//    and to be included by another file, e.g. ~/portland/schedules.php.
//    The following is an example of ~/portland/schedules.php:
//
//			include("./info.php");
//			include("./schedulesql.php");
//
//    where,
//       ./info.php constains related information, such as:
//                             - database username/password,
//                             - ciity name/timezone/query period/etc.
//    so, before including this file, info.php needs to be included.
//
// Query parameters:
//   - stop_id=xxx     required
//   - route_id=xxx    required	
//   - day=YYYYMMDD    optional, by default, it's today
//   Exmaples:
//         http://xxx.xxx.xxx/portalnd/schedules.php?stop_id=10324&route_id=33&day=20081010
//         http://xxx.xxx.xxx/portalnd/schedules.php?stop_id=10324&route_id=33
//
//=============================================================================

///function openDB($dbServer, $dbUser, $dbPass, $dbName)
// Description:
//    Open a database
// Parameters:
//    - $dbServer, host of dbbase
//    - $dbUser,   database user name
//    - $dbPass,   database user password
//    - $dbName,   database name
// Return values:
//    - database connection.
// 
function openDB($dbServer, $dbUser, $dbPass, $dbName)
{
	$link = mysql_connect("$dbServer", "$dbUser", "$dbPass") or die("Failed: Could not connect");
	mysql_select_db("$dbName") or die("Failed: Could not select database");
	return $link;
}


///function queryAShapeAndWriteXML($link, $trip_to_query)
// Description:
//    Query whole day schedule for given routes at a stop, and write XML script.
// Parameters:
//    - $link,            database connection
//    - $stop_to_query,   trip id 
//                        obviously, $queryDate and $queryDay need to be consistent!
// Return values:
//    - None. XML output directly to the page.
// Notes:
//    1. 
//
function queryAShapeAndWriteXML($link, $trip_to_query )
{
	$query = '
				SELECT 
					shapes.shape_id, shape_pt_lat, shape_pt_lon, shape_pt_sequence
				FROM
					shapes, trips
				WHERE
					shapes.shape_id=trips.shape_id AND
					trip_id="' . $trip_to_query . '" 
				ORDER BY
					shape_pt_sequence
				';		
	//print $query;
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	if ($totalRows > 0) { // Show if recordset not empty 
		$currentRow = mysql_fetch_assoc($result);
		do { 
			echo('<shape ');
				echo('shape_id="'); echo $currentRow['shape_id']; echo('" ');
				echo('shape_pt_lat="'); echo $currentRow['shape_pt_lat']; echo('" ');
				echo('shape_pt_lon="'); echo $currentRow['shape_pt_lon']; echo('" ');
				echo('shape_pt_sequence="'); echo $currentRow['shape_pt_sequence']; echo('" ');
			echo('/>');
		} while ($currentRow = mysql_fetch_assoc($result)); 
	} // Show if recordset not empty 	
	
	//Free resultset					
	mysql_free_result($result);
}

///function strToDateTime($date)
// Description:
//    Convert a date from YYYYMMDD format to a system time format,
//      in order to extract weekday information, using system function.
// Parameters:
//    - $date,            'YYYYMMDD'
// Return values:
//    - Time, with Hour:Min:Sec set to 00:00:00. 
//
function strToDateTime($date) 
{
	$dateStr = trim($date);
	$dateTime = array('sec' => 0, 'min' => 0, 'hour' => 0, 'day' => 0, 'mon' => 0, 'year' => 0);
	$dateTime['year'] = substr($date, 0, 4);
	$dateTime['mon'] = substr($date, 4, 2);
	$dateTime['day'] = substr($date, 6, 2);

	return mktime($dateTime['hour'], $dateTime['min'], $dateTime['sec'], $dateTime['mon'], $dateTime['day'], $dateTime['year']);
}

//parse time
$queryBeginTime = time() + ($timeZone * 60 * 60);
$queryBeginTimeStr = '00:00:00';
$queryBeginDateStr = date('Ymd', $queryBeginTime);
$queryBeginDayStr = date('l', $queryBeginTime);

$queryEndTime = $queryBeginTime + ($queryPeriod * 60 * 60);
$queryEndTimeStr = '23:59:59';
$queryEndDateStr = $queryBeginDateStr;
$queryEndDayStr = $queryBeginDayStr;

//Show result
header('Content-type: text/xml');
header('Pragma: public');        
header('Cache-control: private');
header('Expires: -1');
echo('<?xml version="1.0" encoding="utf-8"?>');
echo('<resultSet xmlns="zyao:'.$agencyName.':arrivals" city="'.$cityName.'" queryTime="' . date('Y-m-d H:m:s', $queryBeginTime). '">');

$link = openDB($dbServer, $dbUser, $dbPass, $dbName);

//Parse user parameter
$url = $_SERVER['REQUEST_URI'];
$processed_url = parse_url($url);
$query_string = $processed_url[ 'query' ];
$parameters = explode( '&', $query_string );
foreach( $parameters as $param ){
	$paramAndVales = explode( '=', $param );
	if ($paramAndVales[0] == 'trip_id')	{
		$trips = explode( ',', str_replace('%20', ' ', $paramAndVales[1])) ;
		foreach( $trips as $trip_to_query ){			
			queryAShapeAndWriteXML($link, $trip_to_query, $queryBeginTime, $queryPeriod);	
		}
	}
}

echo('</resultSet>');
?>