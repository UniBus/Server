<?php
//=============================================================================
/// The code in this file queries for arrivals given a stop.
//
//  This file is designed to used as part of the quering script, 
//    and to be included by another file, e.g. ~/portland/arrivals.php.
//    The following is an example of ~/portland/arrivals.php:
//
//			include("./info.php");
//			include("./arrivalsql.php");
//
//    where,
//       ./info.php constains related information, such as:
//                             - database username/password,
//                             - ciity name/timezone/query period/etc.
//    so, before including this file, info.php needs to be included.
//       
//=============================================================================
//
//History for major revisions:
//	- Oct/05/2008, Zhenwang Yao
//		initial version.
//
//	- Oct/26/2008,  Zhenwang Yao
//		major changes on the query scheme, in order to
//		(a)output possible route, even when there is no arrivals within query period
//		(b)limit number of arrivals to ($maxNumOfArrival) for a route at a stop.
//
//	- Nov/15/2008,  Zhenwang Yao
//		major changes on the query scheme, to improve query performance.
//

//User-defined limit on returning arrivals record set for one route at one stop
$maxNumOfArrival = 2;

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
	//Notes: In the query above, query condition does not include date (as in comment), 
	//       which should be included in theory. The reason of doing so
	//       is to avoid problems that may be caused by lazy update.
	//   *** One pitfall though, be careful:
	//       In some data, there may exist multiple periods, corresponding
	//       to difference set of service IDs. Then it may cause problems
	//       like extra/duplicated data.
	// *** that actually happend, so I put it back!!
	
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
		
	//print_r($serviceIds);
	return $serviceIds;
}

///function queryServiceId2($link, $queryDate)
// Description:
//    Return a set of feasible service IDs, which will be used in queryAStopAndWriteXML(...)
// Parameters:
//    - $link,       database connection
//    - $queryDate,  a date to query, in format of 'YYYYMMDD'
// Return values:
//    - service Ids, in form of array.
// Notes:
//    The function returns all possible service ids valid in current period.
//
function queryServiceId2($link, $queryDate)
{
	//Check if there is any feasible service id in calendar
	//Outcomes of this query are a list of service_ids.
	$query = '
				SELECT DISTINCT service_id
				FROM
					calendar
				WHERE
					start_date<="'. $queryDate. '" AND end_date>="'.$queryDate. '"'
				;
	
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
			
	//print_r($serviceIds);
	return $serviceIds;
}

///function routesAtStop($link, $stop_to_query)
// Description:
//    Return all possible routes at a given stop.
// Parameters:
//    - $link,          database connection
//    - $stop_to_query, stop id
//    - $beginTime,     service time
// Return values:
//    - all routes, as an array.
// Notes:
//    - all service doesn't contain the $beginTime will be ignore
function routesAtStop($link, $stop_to_query, $beginTime)
{
	$routesFound = array(); 
	$queryBeginDateStr = date('Ymd', $beginTime);
	$serviceIds = queryServiceId2($link, $queryBeginDateStr );
	if (count($serviceIds)>0) {
		//reindex the array
		$serviceIds = array_values($serviceIds);	
		$calendarPhase = 'trips.service_id IN ("'. $serviceIds[0];
		$count = count($serviceIds);
		for ($i = 1; $i < $count; $i++) {
			$calendarPhase = $calendarPhase . '","'. $serviceIds[$i];
		}
		$calendarPhase = $calendarPhase . '")';
		
		$query = '
					SELECT DISTINCT 
						routes.route_id, routes.route_short_name, routes.route_long_name, trips.trip_headsign, trips.direction_id
					FROM 
						routes, trips, stop_times
					WHERE
						stop_times.stop_id="' . $stop_to_query. '" AND
						stop_times.trip_id=trips.trip_id AND
						routes.route_id=trips.route_id AND '
						.$calendarPhase. '
					GROUP BY route_id, direction_id
					ORDER BY
						route_short_name, route_id, direction_id
					';
		//print $query;					
		$routesAtStop = mysql_query($query, $link) or die('Query failed: '. mysql_error());
		$totalRoutes = mysql_num_rows($routesAtStop);
	
		$currentRouteIndex = 0;
		if ($totalRoutes > 0) { // Show if recordset not empty 
			$currentRoute = mysql_fetch_assoc($routesAtStop);
			do { 
				$routesFound[$currentRouteIndex] = $currentRoute;
				$currentRouteIndex++;
			}while ($currentRoute = mysql_fetch_assoc($routesAtStop));
		}
		mysql_free_result($routesAtStop);

	}// if (count($serviceIds)>=0)
	else
	{
		$query = '
					SELECT DISTINCT 
						routes.route_id, routes.route_short_name, routes.route_long_name, trips.trip_headsign, trips.direction_id
					FROM 
						routes, trips, stop_times
					WHERE
						stop_times.stop_id="' . $stop_to_query. '" AND
						stop_times.trip_id=trips.trip_id AND
						routes.route_id=trips.route_id 
					GROUP BY route_id, direction_id
					ORDER BY
						route_short_name, route_id, direction_id
					';
		//print $query;					
		$routesAtStop = mysql_query($query, $link) or die('Query failed: '. mysql_error());
		$totalRoutes = mysql_num_rows($routesAtStop);
	
		$currentRouteIndex = 0;
		if ($totalRoutes > 0) { // Show if recordset not empty 
			$currentRoute = mysql_fetch_assoc($routesAtStop);
			do { 
				$routesFound[$currentRouteIndex] = $currentRoute;
				$currentRouteIndex++;
			}while ($currentRoute = mysql_fetch_assoc($routesAtStop));
		}
		mysql_free_result($routesAtStop);
	}

	//print_r($routesFound);
	return $routesFound;
}

///function queryRoutesAtAStop($link, $stop_to_query, $routes_to_query, $beginTime, $duration)
// Description:
//    Query arrivals for a given route at a given stop.
// Parameters:
//    - $link,            database connection
//    - $stop_to_query,   stop id 
//    - $routes_to_query, route ids 
//    - $beginTime,       starting time of query period
//    - $duration,        duration of query period
// Return values:
//    - a set of arrivals, as an array, actually a dictionary:
//      [*] key of the element is route_id
//      [*] value of the dictionary is an ARRAY, the real arrivals
// Notes:
//    1. The time for a service may go beyond '23:59:00', for example, it can be '27:00:00',
//       indicating the service last beyond midnight of the day. 
//       So, imposing $endTime in the query may not be good idea, and we ignore $endTime in the query.
//
function queryRoutesAtAStop($link, $stop_to_query, $routes_to_query, $beginTime, $duration )
{
	global $maxNumOfArrival;
	
	$queryBeginTimeStr = date('H:i:s', $beginTime);
	$queryBeginDateStr = date('Ymd', $beginTime);
	$queryBeginDayStr = date('l', $beginTime);
	
	//Set up the empty structure of arrivals
	$arrivals = array(); 
	foreach ($routes_to_query as $aRoute) {
		$arrivals[$aRoute['route_id'].'_'.$aRoute['direction_id']] = array();
	}
	
	//Get a set of feasible service IDs
	$serviceIds = queryServiceId($link, $queryBeginDateStr, $queryBeginDayStr );
	if (count($serviceIds)>0) {
		//reindex the array
		$serviceIds = array_values($serviceIds);	
		$calendarPhase = 'trips.service_id IN ("'. $serviceIds[0];
		$count = count($serviceIds);
		for ($i = 1; $i < $count; $i++) {
			$calendarPhase = $calendarPhase . '","'. $serviceIds[$i];
		}
		$calendarPhase = $calendarPhase . '")';
		
		//Query for arrivals
		//Notes about DISTINCT:
		//	Add Nov-11-2008, there are some duplication in Milwaukee data.
		//  IMO, data should be fixed, instead of the code.
		$query = '
					SELECT DISTINCT
							routes.route_id, stop_times.stop_headsign, trips.trip_headsign, stop_times.arrival_time, trips.direction_id
					FROM
							stop_times, trips, routes
					WHERE
							stop_id="' . $stop_to_query . '" AND
							stop_times.trip_id=trips.trip_id AND 
							trips.route_id = routes.route_id AND ' 
							.$calendarPhase. ' AND	
							stop_times.arrival_time>="' . $queryBeginTimeStr . '"
					ORDER BY
							arrival_time
					' 
					;		
		//print $query;
		$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
		$totalRows= mysql_num_rows($result);
	
		if ($totalRows > 0) { // Show if recordset not empty 
			$currentRow = mysql_fetch_assoc($result);
			do { 
				$arrivalsForTheRoute = &$arrivals[$currentRow['route_id'].'_'.$currentRow['direction_id']];
				if (count($arrivalsForTheRoute) < $maxNumOfArrival) {
					array_push($arrivalsForTheRoute, $currentRow);
				}
			} while ($currentRow = mysql_fetch_assoc($result)); 
		} // Show if recordset not empty 		
		//Free resultset					
		mysql_free_result($result);	
		//print_r($arrivals);
	}// if (count($serviceIds)>=0)
	
	//If having got enough of record, then return,
	//otherwise, check if need to look at tomorrow's arrivals
	$allRoutesReachMax = TRUE;
	foreach ($arrivals as $arrivalsOfARoute) {
		if (count($arrivalsOfARoute) < $maxNumOfArrival) {
			$allRoutesReachMax = FALSE;
			break;
		}
	}
	if ($allRoutesReachMax) {
		return $arrivals;
	}

	$endTime = $beginTime + ($duration * 60 * 60);
	$queryEndTimeStr = date('H:i:s', $endTime);
	$queryEndDateStr = date('Ymd', $endTime);
	$queryEndDayStr = date('l', $endTime);

	//If it turns out that query period falls in the same day, then return
	if ($queryBeginDateStr == $queryEndDateStr)
		return $arrivals;
	
	//Query for "tomorrow"s arrivals.
	//$calendarPhase = queryServiceId($link, $queryEndDateStr, $queryEndDayStr );
	$serviceIds = queryServiceId($link, $queryEndDateStr, $queryEndDayStr  );
	if (count($serviceIds)>0) {
		//reindex the array
		$serviceIds = array_values($serviceIds);
		
		$calendarPhase = 'trips.service_id IN ("'. $serviceIds[0];
		$count = count($serviceIds);
		for ($i = 1; $i < $count; $i++) {
			$calendarPhase = $calendarPhase . '","'. $serviceIds[$i];
		}
		$calendarPhase = $calendarPhase . '")';
		$query = '
					SELECT DISTINCT 
							routes.route_id, stop_times.stop_headsign, trips.trip_headsign, stop_times.arrival_time, trips.direction_id
					FROM
							stop_times, trips, routes
					WHERE
							stop_id="' . $stop_to_query . '" AND
							stop_times.trip_id=trips.trip_id AND 
							trips.route_id = routes.route_id AND ' 
							.$calendarPhase. ' AND	
							stop_times.arrival_time<="' . $queryEndTimeStr . '" 
					ORDER BY
							arrival_time
					'
					;
						
		//print $query;
		$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
		$totalRows= mysql_num_rows($result);
		if ($totalRows > 0) { // Show if recordset not empty 
			$currentRow = mysql_fetch_assoc($result);
			do {
				$currentKey = $currentRow['route_id'].'_'.$currentRow['direction_id'];
				if (array_key_exists($currentKey, $arrivals)) { 
					$arrivalsForTheRoute = &$arrivals[$currentKey];
					if (count($arrivalsForTheRoute) < $maxNumOfArrival) {
						array_push($arrivalsForTheRoute, $currentRow);
					}
				}	
			} while ($currentRow = mysql_fetch_assoc($result)); 
		} // Show if recordset not empty 	
		mysql_free_result($result);
	}
	
	//print_r($arrivals);
	return $arrivals;	
}

///function queryAStopAndWriteXML($link, $stop_to_query, $beginTime, $duration)
// Description:
//    Query arrivals for a stop, and write XML script.
// Parameters:
//    - $link,          database connection
//    - $stop_to_query, stop id 
//    - $beginTime,     starting time of query period
//    - $duration,      duration of query period
// Return values:
//    - None. XML output directly to the page.
// Notes:
//    1. Output XML contains only arrivals info, and header and footer of XML
//       is written by the caller of this function.
// Known Problem: (****)
//    1. For some particular cities, there may be empty calendar table,
//       which causes problem of getting an empty arrival set.
//       Currently approach to walk around this is to manually add a fake record into the calendar table,
//       but this need more investigate in the future.
//    2. For some cities, there may be duplication between calendar and caleedar_date:
//       a service is on for the $queryDay, and it again added in calendar_date for the $queryDate.
//       This also caused problem, and got duplicated records.
//       I fixed the problem, but couldn't remember how. [be aware of that!]
//
function queryAStopAndWriteXML($link, $stop_to_query, $beginTime, $duration)
{
	//Get all route at the stop
	$routes = routesAtStop($link, $stop_to_query, $beginTime);
	//Get route arrivals at the stop
	$arrivals = queryRoutesAtAStop($link, $stop_to_query, $routes, $beginTime, $duration );
	
	//Go through these routes one by one!
	//print_r($routes);
	$routeNamesPrinted = array();
	foreach($routes as $theRoute){
		$route_to_query = $theRoute["route_id"].'_'.$theRoute['direction_id'];
		//Get route arrivals at the stop
		$arrivalsOfTheRoute = &$arrivals[$route_to_query];
		//If get arrivals, output
		if (count($arrivalsOfTheRoute) > 0){
			//print_r($arrivalsOfTheRoute);
			foreach($arrivalsOfTheRoute as $anArrival){	
				echo('<arrival ');
					echo('stop_id="'); echo $stop_to_query; echo('" ');
					echo('route_id="'); echo $theRoute["route_id"]; echo('" ');
					echo('route_name="'); 
						if ($theRoute['route_short_name'] != ''){
							echo $theRoute['route_short_name']; 
							array_push($routeNamesPrinted, $theRoute['route_short_name']);
						}
						else{
							echo $theRoute['route_long_name']; 
							array_push($routeNamesPrinted, $theRoute['route_long_name']);
						}
					echo('" ');
					echo('bus_sign="'); 
						if ($anArrival['stop_headsign'] != ''){
							echo $anArrival['stop_headsign'];
						}else if ($anArrival['trip_headsign'] != ''){
							echo $anArrival['trip_headsign']; 
						} else {
							echo $theRoute['route_long_name']; 
						}
					echo('" ');
					echo('direction_id="'); echo $anArrival['direction_id']; echo('" ');
					echo('arrival_time="'); echo $anArrival['arrival_time']; echo('" ');
				echo('/>');
			}
		}
	}//foreach($routes as $theRoute)
	foreach($routes as $theRoute){
		$route_to_query = $theRoute["route_id"].'_'.$theRoute['direction_id'];
		//Get route arrivals at the stop
		$arrivalsOfTheRoute = &$arrivals[$route_to_query];
		//If get arrivals, output
		if (count($arrivalsOfTheRoute) > 0)
			continue;
		
		$nameToPrint = '';
		if ($theRoute['route_short_name'] != '')
			$nameToPrint = $theRoute['route_short_name']; 
		else
			$nameToPrint = $theRoute['route_long_name']; 
		
		$nameUsedBefore = false;
		foreach($routeNamesPrinted as $namePrinted) {
			if ($namePrinted == $nameToPrint)
			{
				$nameUsedBefore = true;
				break;
			}
		}

		if ($nameUsedBefore == true)
			continue;

		//No arrivalsOfTheRoute? then output basic info!
		echo('<arrival ');
			echo('stop_id="'); echo $stop_to_query; echo('" ');
			echo('route_id="'); echo $theRoute["route_id"]; echo('" ');
			echo('route_name="'); echo $nameToPrint; echo('" ');
			echo('bus_sign="'); 
				if ($theRoute['trip_headsign'] != '')
					echo $theRoute['trip_headsign']; 
				else
					echo $theRoute['route_long_name']; 
			echo('" ');
			echo('direction_id="'); echo $theRoute['direction_id']; echo('" ');
			echo('arrival_time="--:--:--"'); 
		echo('/>');
	} //foreach($routes as $theRoute)
}


//query time
$queryBeginTime = time() + ($timeZone * 60 * 60) - 60;

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
$stops = explode( '=', $query_string );
if ($stops[0] == 'stop_id'){
	$stopids = 	explode( ',', str_replace('%20', ' ', $stops[1]) );
	foreach( $stopids as $stop_to_query ){			
		queryAStopAndWriteXML($link, $stop_to_query, $queryBeginTime, $queryPeriod);	
	}
}

echo('</resultSet>');
?>
