<?php
function openDB($dbServer, $dbUser, $dbPass, $dbName)
{
	$link = mysql_connect("$dbServer", "$dbUser", "$dbPass") or die("Failed: Could not connect");
	mysql_select_db("$dbName") or die("Failed: Could not select database: ".$dbName);
	return $link;
}

function closeDB($link)
{
	mysql_close($link);
}

function queryCityAgency($city)
{
	$cityDBServer='localhost';
	$dbUser='root';
	$dbPass='youneedpasswod';
	$dbName='bus_'.$city;
	$cityDBLink = openDB($cityDBServer, $cityDBUser, $cityDBPass, $cityDBName);
	
	$query = 'SELECT agency_name FROM agency';
	$result = mysql_query($query, $cityDBLink) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	$agencyNames = '';
	if ($totalRows > 0) { // Show if recordset not empty 
		$currentRow = mysql_fetch_assoc($result);
		do { 
			if ($agencyNames == ''){
				$agencyNames = $currentRow['agency_name'];
			}
			else{
				$agencyNames = $agencyNames.'<br>'.$currentRow['agency_name'];
			}
		} while ($currentRow = mysql_fetch_assoc($result)); 
	} // Show if recordset not empty 	
	mysql_free_result($result);
	
	//closeDB($cityDBLink);
	return $agencyNames;
}

function GetDeltaTime($dtTime1, $dtTime2)
{
	$nUXDate1 = strptime($dtTime1, "Ymd");
	$nUXDate2 = strptime($dtTime2, "Ymd");

	$nUXDelta = $nUXDate1 - $nUXDate2;
	$dDeltaTime = "" . $nUXDelta/60/60/24; // sec -> day
	   
	return $dDeltaTime;
}

function queryCityExpirary($city)
{
	$cityDBServer='localhost';
	$dbUser='root';
	$dbPass='youneedpasswod';
	$dbName='bus_'.$city;
	$cityDBLink = openDB($cityDBServer, $cityDBUser, $cityDBPass, $cityDBName);
	
	$query = 'SELECT service_id,start_date,end_date FROM calendar ORDER BY end_date DESC';
	$result = mysql_query($query, $cityDBLink) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	$expiredDate = '';
	if ($totalRows > 0) { // Show if recordset not empty 
		$currentRow = mysql_fetch_assoc($result);
		$expiredDate = $currentRow['end_date'];
	} // Show if recordset not empty 	
	mysql_free_result($result);
	
	if ($expiredDate != ''){
	return $expiredDate;
	}

	$query = 'SELECT service_id, date FROM calendar_dates ORDER BY date DESC';
	$result = mysql_query($query, $cityDBLink) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	if ($totalRows > 0) { // Show if recordset not empty 
		$currentRow = mysql_fetch_assoc($result);
		$expiredDate = $currentRow['date'];
	} // Show if recordset not empty 	
	mysql_free_result($result);

	//closeDB($cityDBLink);
	return $expiredDate;
}

function listAllCities()
{
	$dbServer='localhost';
	$dbUser='root';
	$dbPass='youneedpasswod';
	$dbName='gtfs_info_v12';
	$link = openDB($dbServer, $dbUser, $dbPass, $dbName);

	$query = 'SELECT * FROM cities ORDER BY country, state, name';
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	$citiesFound = array(); 
	if ($totalRows > 0) { // Show if recordset not empty 
	    $currentRow = mysql_fetch_assoc($result);
	    do { 
		//echo('<td>'); echo $currentRow['id']; echo('</td>');
		$cityId = $currentRow['id'];
		$cityName = $currentRow['name'].', '. $currentRow['state'].', '. $currentRow['country'];
		$citiesFound[$cityName] = $cityId;
	    } while ($currentRow = mysql_fetch_assoc($result)); 
	} // Show if recordset not empty 	
	
	//Free resultset					
	mysql_free_result($result);

	return $citiesFound;
}

function getRandomStop($link)
{
	$query = 'SELECT * FROM stops ORDER BY RAND() LIMIT 1';
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	$stopFound = array(); 
	if ($totalRows > 0) { // Show if recordset not empty 
	    $currentRow = mysql_fetch_assoc($result);
	    $stopFound['stop_id'] = $currentRow['stop_id'];
	    $stopFound['stop_name'] = $currentRow['stop_name'];
	    $stopFound['stop_lon'] = $currentRow['stop_lon'];
	    $stopFound['stop_lat'] = $currentRow['stop_lat'];
	} // Show if recordset not empty 	
	
	//Free resultset					
	mysql_free_result($result);

	return $stopFound;
}

function getRandomRoute($link)
{
	$query = 'SELECT route_id, route_short_name route_long_name FROM routes ORDER BY RAND() LIMIT 1';
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	$routeFound = array(); 
	if ($totalRows > 0) { // Show if recordset not empty 
	    $currentRow = mysql_fetch_assoc($result);
	    $routeFound['route_id'] = $currentRow['route_id'];
	    $routeFound['route_short_name'] = $currentRow['route_short_name'];
	    $routeFound['route_long_name'] = $currentRow['route_long_name'];
	} // Show if recordset not empty 	
	
	//Free resultset					
	mysql_free_result($result);

	return $routeFound;
}

function getRandomTrip($link)
{
	$query = 'SELECT trip_id, trip_headsign, route_id, direction_id FROM trips ORDER BY RAND() LIMIT 1';
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	$tripFound = array(); 
	if ($totalRows > 0) { // Show if recordset not empty 
	    $currentRow = mysql_fetch_assoc($result);
	    $tripFound['trip_id'] = $currentRow['trip_id'];
	    $tripFound['route_id'] = $currentRow['route_id'];
	    $tripFound['direction_id'] = $currentRow['direction_id'];
	    $tripFound['trip_headsign'] = $currentRow['trip_headsign'];
	    if ($tripFound['trip_headsign'] == '')
	       $tripFound['trip_headsign'] = '(No Headsign)';
	} // Show if recordset not empty 	
	
	//Free resultset					
	mysql_free_result($result);

	return $tripFound;
}

function getRandomTrip2($link)
{
	$randomTrip = getRandomTrip($link);
	$query = 'SELECT stop_id FROM stop_times WHERE trip_id="'. $randomTrip['trip_id']. '" ORDER BY RAND() LIMIT 1';
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	$tripFound = array(); 
	if ($totalRows > 0) { // Show if recordset not empty 
	    $currentRow = mysql_fetch_assoc($result);
	    $tripFound['trip_id'] = $randomTrip['trip_id'];
	    $tripFound['route_id'] = $randomTrip['route_id'];
	    $tripFound['direction_id'] = $randomTrip['direction_id'];
	    $tripFound['stop_id'] = $currentRow['stop_id'];
	    $tripFound['trip_headsign'] = $randomTrip['trip_headsign'];
	} // Show if recordset not empty 	
	
	//Free resultset					
	mysql_free_result($result);

	return $tripFound;
}

function writeRandomTestHTMLStop($city, $items)
{
	$dbServer='localhost';
	$dbUser='root';
	$dbPass='youneedpasswod';
	$dbName='bus_'.$city;
	$link = openDB($dbServer, $dbUser, $dbPass, $dbName);

	echo '<ul>';
	for ($i=1; $i<=5; $i++) {
		$randomStop = getRandomStop($link);
		echo '<li><a href=http://unibus.ca:5144/ver1.2/'.$city.'/arrivals.php?stop_id='.$randomStop['stop_id'].'>'.$randomStop['stop_name'].'</a>'.
		        ' [<a href=http://unibus.ca:5144/ver1.2/'.$city.'/stopmap.php?lat='.$randomStop['stop_lat'].'&long='.$randomStop['stop_lon'].'>map</a>]'.
		     '</li>';
	}
	echo '</ul>';

	closeDb($link);
}

function writeRandomTestHTMLSchedule($city, $items)
{
	$dbServer='localhost';
	$dbUser='root';
	$dbPass='youneedpasswod';
	$dbName='bus_'.$city;
	$link = openDB($dbServer, $dbUser, $dbPass, $dbName);

	echo '<ul>';
	for ($i=1; $i<=5; $i++) {
		$randomTrip = getRandomTrip2($link);
		echo '<li><a href=http://unibus.ca:5144/ver1.2/'.$city.'/schedules.php?stop_id='.$randomTrip['stop_id'].
			'&route_id='.$randomTrip['route_id'].'&direction_id='.$randomTrip['direction_id'].
			'>'.$randomTrip['route_id'].'@'.$randomTrip['stop_id'].' ('. $randomTrip['trip_headsign'] .')' .'</a></li>';
	}
	echo '</ul>';

	closeDb($link);
}

function writeRandomTestHTMLRoute($city, $items)
{
	$dbServer='localhost';
	$dbUser='root';
	$dbPass='youneedpasswod';
	$dbName='bus_'.$city;
	$link = openDB($dbServer, $dbUser, $dbPass, $dbName);

	echo '<ul>';
	for ($i=1; $i<=5; $i++) {
		$randomRoute = getRandomRoute($link);
		echo '<li><a href=http://unibus.ca:5144/ver1.2/'.$city.'/tripsofroute.php?route_id='.$randomRoute['route_id'].'>'.$randomRoute['route_short_name'].' (' . $randomRoute['route_long_name']. ')'.'</a></li>';
	}
	echo '</ul>';
	closeDb($link);
}

function writeRandomTestHTMLTrip($city, $items)
{
	$dbServer='localhost';
	$dbUser='root';
	$dbPass='youneedpasswod';
	$dbName='bus_'.$city;
	$link = openDB($dbServer, $dbUser, $dbPass, $dbName);

	echo '<ul>';
	for ($i=1; $i<=5; $i++) {
		$randomTrip = getRandomTrip($link);
		echo '<li><a href=http://unibus.ca:5144/ver1.2/'.$city.'/routemap.php?trip_id='.$randomTrip['trip_id'].'>'.$randomTrip['route_id'].' (' . $randomRoute['trip_headsign']. ')'.'</a></li>';
	}
	echo '</ul>';
	closeDb($link);
}

?>
