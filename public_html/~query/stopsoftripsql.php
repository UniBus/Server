<?php
//=============================================================================
/// The code in this file queries stops along a route, given either
//   - (trip_id), or
//   - (route_id, direction_id, headsign)
//
//  This file is designed to used as part of the quering script, 
//    and to be included by another file, e.g. ~/oc/stopsoftrip.php.
//    The following is an example of ~/oc/stopsoftrip.php:
//
//			include("./info.php");
//			include("./stopsoftripsql.php");
//
//    where,
//       ./info.php constains related information, such as:
//                             - database username/password,
//                             - ciity name/timezone/query period/etc.
//    so, before including this file, info.php needs to be included.
//
// Query parameters:
//   - (trip_id=xxx), or
//   - (route_id=xxx, direction-id=xxx, headsign=xxx)
//   Exmaples:
//         http://xxx.xxx.xxx/ver1.3/oc/stopsoftrip.php?route_id=172&direction_id=&headsign=Huntington Beach to Costa Mesa
//         http://xxx.xxx.xxx/ver1.3/oc/stopsoftrip.php?route_id=172&direction_id=
//         http://xxx.xxx.xxx/ver1.3/oc/stopsoftrip.php?trip_id=2964049
//
// Output format:
//       <resultSet city="Orange-Country" queryTime="10:09:48">
//            <trip trip_id="2964049" route_id="172" direction_id="" head_sign="Huntington Beach to Costa Mesa"/>
//            <stop stop_id="1116"/>
//            ... skip ...
//            <stop stop_id="7697"/>
//       </resultSet>
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


///function queryATripAndWriteXML($link, $trip_to_query)
// Description:
//    Query stops along the way given a trip_id, and write XML script.
// Parameters:
//    - $link,            database connection
//    - $trip_to_query,   trip id 
// Return values:
//    - None. XML output directly to the page. . See above for XML format.
// Notes:
//    1. 
//
function queryATripAndWriteXML( $link, $trip_to_query )
{
	$query = '
			SELECT *
			FROM trips
			WHERE trip_id="' . $trip_to_query . '" 
			LIMIT 1
		';		
	//print $query;
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);
	if ($totalRows > 0) {
		$theTrip = mysql_fetch_assoc($result);
		$routeId = $theTrip['route_id'];
		$dirId = $theTrip['direction_id'];
		$headSign = $theTrip['trip_headsign'];		
	} // Show if recordset not empty 
	mysql_free_result($result);
	
	$query = '
			SELECT
				stop_id
			FROM
				stop_times
			WHERE
				trip_id="' . $trip_to_query . '"  
		';		
	//print $query;
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	if ($totalRows > 0) { // Show if recordset not empty 
		echo('<trip ');
			echo('trip_id="'); echo $trip_to_query; echo('" ');
			echo('route_id="'); echo $routeId; echo('" ');
			echo('direction_id="'); echo $dirId; echo('" ');
			echo('head_sign="'); echo $headSign; echo('" ');
		echo('/>');
		$currentRow = mysql_fetch_assoc($result);
		do {
			echo('<stop ');
				//echo('trip_id="'); echo $trip_to_query; echo('" ');
				echo('stop_id="'); echo $currentRow['stop_id']; echo('" ');
			echo('/>');
		} while ($currentRow = mysql_fetch_assoc($result)); 
	} // Show if recordset not empty 	
	
	//Free resultset					
	mysql_free_result($result);
}


///function queryARouteDirAndWriteXML( $link, $route_to_query, $dir_to_query, $sign_to_query )
// Description:
//    Query stops along the way given a (route_id, dir_id, headsign), and write XML script.
// Parameters:
//    - $link,            database connection
//    - $route_to_query,  route id 
//    - $dir_to_query,    direction id 
//    - $sign_to_query,   bus sign 
// Return values:
//    - None. XML output directly to the page. See above for XML format.
// Notes:
//    1. Two types of info to get
//       - get trip_id/info, from given (route_id, direction_id, headsign)
//       - get all stop_ids along the trip
//    2. Querying with head_sign is a bit tricky, since every city has different definition.
//
function queryARouteDirAndWriteXML( $link, $route_to_query, $dir_to_query, $sign_to_query )
{
	$query = '
			SELECT
				trips.trip_id, trips.trip_headsign, routes.route_short_name, routes.route_long_name
			FROM
				stop_times, trips, routes
			WHERE
				trips.route_id="' . $route_to_query . '" AND 
				trips.direction_id="' . $dir_to_query . '" AND 
				trips.trip_id=stop_times.trip_id AND 					
				routes.route_id = trips.route_id AND
				(trips.trip_headsign ="' . $sign_to_query . '" OR 
				 routes.route_long_name ="' . $sign_to_query . '" OR
				 routes.route_short_name ="' . $sign_to_query . '")
			LIMIT 1
			';		
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	$tripId = '';
	$tripSign = '' ;
	if ($totalRows == 0){
		$query = '
				SELECT
					trips.trip_id, trips.trip_headsign, routes.route_short_name, routes.route_long_name
				FROM
					stop_times, trips, routes
				WHERE
					trips.route_id="' . $route_to_query . '" AND 
					trips.direction_id="' . $dir_to_query . '" AND 
					trips.trip_id=stop_times.trip_id AND
					routes.route_id = trips.route_id 
				LIMIT 1
				';		
		$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
		$totalRows= mysql_num_rows($result);
	}

	if ($totalRows == 1){
		$currentRow = mysql_fetch_assoc($result);
		$tripId = $currentRow['trip_id'];
		//queryATripAndWriteXML($link, $tripId);		
		if ($currentRow['trip_headsign'] != ''){
			$tripSign = $currentRow['trip_headsign']; 
		} else if ($currentRow['route_long_name'] != '') {
			$tripSign =  $currentRow['route_long_name']; 
		} else {
			$tripSign =  $currentRow['route_short_name']; 
		}
	}
	//Free resultset					
	mysql_free_result($result);

	if ($tripId != ''){
		$query = '
				SELECT
					stop_id
				FROM
					stop_times
				WHERE
					trip_id="' . $tripId . '"  
				';		
		//print $query;
		//return;
		$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
		$totalRows= mysql_num_rows($result);

		if ($totalRows > 0) { // Show if recordset not empty 
			$currentRow = mysql_fetch_assoc($result);
			echo('<trip ');
				echo('trip_id="'); echo $tripId; echo('" ');
				echo('route_id="'); echo $route_to_query; echo('" ');
				echo('direction_id="'); echo $dir_to_query; echo('" ');
				echo('head_sign="'); echo $tripSign; echo('" ');
			echo('/>');
			do {
				echo('<stop ');
					echo('stop_id="'); echo $currentRow['stop_id']; echo('" ');
				echo('/>');
			} while ($currentRow = mysql_fetch_assoc($result)); 
		} // Show if recordset not empty 
	}
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
echo('<resultSet xmlns="zyao:'.$agencyName.':arrivals" city="'.$cityName.'" queryTime="' . date('H:i:s', $queryBeginTime). '">');

$link = openDB($dbServer, $dbUser, $dbPass, $dbName);

//Parse user parameter
$url = $_SERVER['REQUEST_URI'];
$processed_url = parse_url($url);
$query_string = $processed_url[ 'query' ];
$parameters = explode( '&', str_replace("%20", " ", $query_string) );
$tripId = '';
$routeId = '';
$dirId = '';
$headSign = '';
foreach( $parameters as $param ){
	$paramAndVales = explode( '=', $param );
	if ($paramAndVales[0] == 'trip_id')	{
		$tripId = $paramAndVales[1];
	}
	elseif ($paramAndVales[0] == 'route_id')	{
		$routeId = $paramAndVales[1];
	}
	elseif ($paramAndVales[0] == 'direction_id')	{
		$dirId = $paramAndVales[1];
	}
	else if ($paramAndVales[0] == 'headsign')	{
		$headSign = $paramAndVales[1];
	}
}

if ($tripId != '') {
	queryATripAndWriteXML($link, $tripId);	
}
else if (route_id != '')
{
	queryARouteDirAndWriteXML($link, $routeId, $dirId, $headSign);	
}

echo('</resultSet>');
?>

