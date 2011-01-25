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

///function queryServiceId($link, $queryDate, $queryDay )
// Description:
//    Return a set of feasible service IDs, which will be used in queryAStopAndWriteXML(...)
// Parameters:
//    - $link,       database connection
//    - $queryDate,  a date to query, in format of 'YYYYMMDD'
//    - $queryDay,   a weekday to query, in format of 'monday'/'tuesday'/etc.
//        obviously, $queryDate and $queryDay need to be consistent!
// Return values:
//    - service Ids, in form of array.
// Notes:
//    The function involves two tables: calendar, and calendar_dates
//      - calendar defines weekly schedule of a service
//      - calendar_dates has higher priority, a service may be added or removed
//          for a particular day.
//
function queryServiceId($link, $queryDate, $queryDay )
{
	//Check if there is any feasible service id in calendar
	//Outcomes of this query are a list of service_ids.
	$query = '
				SELECT DISTINCT service_id
				FROM
					calendar
				WHERE					
					start_date<="'. $queryDate. '" AND end_date>="'.$queryDate. '" AND '.$queryDay.'=1'				
					//'.$queryDay.'=1'									
				;
	//Notes: arrivals.php uses same function, check out comments in there!, 
	
	//print $query;
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);
	$serviceIds = array();
	if ($totalRows > 0) { // Show if recordset not empty 
		$currentRow = mysql_fetch_assoc($result);
		do {
			array_push($serviceIds, $currentRow['service_id']);
		} while ($currentRow = mysql_fetch_assoc($result));
	} // Show if recordset not empty 	
	//Free resultset					
	mysql_free_result($result);
	
	//Then, check if the day has been particularly added or removed from some services
	//Outcomes of this query are a list of service_ids with exceptions.
	$query = '
				SELECT service_id, date, exception_type
				FROM
					calendar_dates
				WHERE
					date="' . $queryDate . '"'
				;		
	//print $query;
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);
	$exceptionIds = array();
	if ($totalRows > 0) { // Show if recordset not empty 
		$currentRow = mysql_fetch_assoc($result);
		do {
			$exceptionIds[$currentRow['service_id']] = $currentRow['exception_type'];
		} while ($currentRow = mysql_fetch_assoc($result));
	} // Show if recordset not empty 	
	//Free resultset					
	mysql_free_result($result);

	//Modify serviceIds based on exceptionIds.
	$serviceIdKeys = array_keys($serviceIds);
	foreach ($serviceIdKeys as $existingKey) {
		//if an existingId in seriviceIds has exception. 
		$existingId = $serviceIds[$existingKey];
		if (array_key_exists($existingId, $exceptionIds)){
			//back up the key, in case $existingId maybe unset later.
			$existingIdBackup = $existingId;
			//and if the exception is be 2. 
			if ($exceptionIds[$existingId] == 2) {
				//then, remove existingId from serviceIds.
				unset($serviceIds[$existingKey]);
			}
			unset($exceptionIds[$existingIdBackup]);
		}
	}
	foreach (array_keys($exceptionIds) as $remainingId) {
		if ($exceptionIds[$remainingId] == 1)
			array_push($serviceIds, $remainingId);
	}
		
	//print $serviceIds;
	return $serviceIds;
}

///function queryAStopAndWriteXML($link, $stop_to_query, $routes_to_query, $queryDate, $queryDay )
// Description:
//    Query whole day schedule for given routes at a stop, and write XML script.
// Parameters:
//    - $link,            database connection
//    - $stop_to_query,   stop id 
//    - $routes_to_query, given route Ids
//    - $queryDate,       a date to query, in format of 'YYYYMMDD'
//    - $queryDay,        a weekday to query, in format of 'monday'/'tuesday'/etc.
//                        obviously, $queryDate and $queryDay need to be consistent!
// Return values:
//    - None. XML output directly to the page.
// Notes:
//    1. Output XML contains only arrivals info, and header and footer of XML
//       is written by the caller of this function.
//    2. The time for a service may go beyond '23:59:00', for example, it can be '27:00:00',
//       indicating the service last beyond midnight of the day. 
//       So, imposing $endTime in the query may not be good idea, and we ignore $endTime in the query.
//
function queryAStopAndWriteXML($link, $stop_to_query, $route_to_query, $dir_to_query, $queryDate, $queryDay )
{
	//Get condition clause (for WHERE) for all routes.
	$serviceIds = queryServiceId($link, $queryDate, $queryDay );
	if (count($serviceIds)==0) {
		return;
	}
	
	//reindex the array
	$serviceIds = array_values($serviceIds);	
	$calendarPhase = 'trips.service_id IN ("'. $serviceIds[0];
	$count = count($serviceIds);
	for ($i = 1; $i < $count; $i++) {
		$calendarPhase = $calendarPhase . '","'. $serviceIds[$i];
	}
	$calendarPhase = $calendarPhase . '")';

	//if ($dir_to_query
	//$directionPhase =
	
	$query = '
				SELECT DISTINCT 
					stop_times.stop_id, trips.route_id, stop_times.stop_headsign, trips.trip_headsign, stop_times.arrival_time, routes.route_short_name, routes.route_long_name, trips.direction_id
				FROM
					stop_times, trips, routes
				WHERE
					stop_id="' . $stop_to_query . '" AND
					stop_times.trip_id=trips.trip_id AND 
					(trips.direction_id="'.$dir_to_query.'" OR trips.direction_id="") AND 
					routes.route_id = trips.route_id AND routes.route_id="'.$route_to_query.'" AND '
					. $calendarPhase .' 					
				ORDER BY
					arrival_time, route_id, trip_headsign
				';		
	//print $query;
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	if ($totalRows > 0) { // Show if recordset not empty 
		$currentRow = mysql_fetch_assoc($result);
		do { 
			echo('<arrival ');
				echo('stop_id="'); echo $currentRow['stop_id']; echo('" ');
				echo('route_id="'); echo $currentRow['route_id']; echo('" ');
				echo('route_name="'); 
					if ($currentRow['route_short_name'] != ''){
						echo $currentRow['route_short_name']; 
					}
					else{
						echo $currentRow['route_long_name']; 
					}
				echo('" ');
				echo('bus_sign="'); 
					if ($currentRow['stop_headsign'] != ''){
						echo $currentRow['stop_headsign'];
					}else if ($currentRow['trip_headsign'] != ''){
						echo $currentRow['trip_headsign']; 
					} else {
						echo $currentRow['route_long_name']; 
					}
				echo('" ');
				echo('direction_id="'); echo $currentRow['direction_id']; echo('" ');
				echo('arrival_time="'); echo $currentRow['arrival_time']; echo('" ');
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
$queryTime = time() + ($timeZone * 60 * 60);
$queryDateStr = date('Ymd', $queryTime);
$queryDayStr = date('l', $queryTime);

//Show result
header('Content-type: text/xml');
header('Pragma: public');        
header('Cache-control: private');
header('Expires: -1');
echo('<?xml version="1.0" encoding="utf-8"?>');
echo('<resultSet xmlns="zyao:'.$agencyName.':arrivals" city="'.$cityName.'" queryTime="' . date('Y-m-d H:i:s', $queryTime). '">');

$link = openDB($dbServer, $dbUser, $dbPass, $dbName);

//Parse user parameter
$url = $_SERVER['REQUEST_URI'];
$processed_url = parse_url($url);
$query_string = $processed_url[ 'query' ];
$parameters = explode( '&', $query_string );
$route = '';
$direction = '';
foreach( $parameters as $param ){
	$paramAndVales = explode( '=', $param );
	if ($paramAndVales[0] == 'stop_id')	{
		$stops = explode( ',', str_replace('%20', ' ', $paramAndVales[1])) ;
	}
	else if ($paramAndVales[0] == 'route_id'){
		$route = $paramAndVales[1];
	}
	else if ($paramAndVales[0] == 'direction_id'){
		$direction = $paramAndVales[1] ;
	}
	else if ($paramAndVales[0] == 'day'){
		//Without 'day' parameter, the querying time (today) is the default value
		$queryTime = strToDateTime($paramAndVales[1]);; 
		$queryDateStr = date('Ymd', $queryTime);
		$queryDayStr = date('l', $queryTime);
	}
}

//$stops = explode( '=', $query_string );
//if ($stops[0] == 'stop_id'){
//	$stopids = 	explode( ',', $stops[1] );
foreach( $stops as $stop_to_query ){
	if ($route != '')		
		queryAStopAndWriteXML($link, $stop_to_query, $route, $direction, $queryDateStr, $queryDayStr);
}

echo('</resultSet>');
?>