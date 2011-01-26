<?php
function openDB($dbServer, $dbUser, $dbPass, $dbName)
{
	$link = mysql_connect("$dbServer", "$dbUser", "$dbPass") or die("Failed: Could not connect");
	mysql_select_db("$dbName") or die("Failed: Could not select database");
	return $link;
}

function closeDB($link)
{
	mysql_close($link);
}

function queryCityAgency($city)
{
	$cityDBServer='localhost';
	$cityDBUser='root';
	$cityDBPass='r00tp@ssw0rd';
	$cityDBName='bus_'.$city;
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
	$cityDBUser='root';
	$cityDBPass='youneedpasswod';
	$cityDBName='bus_'.$city;
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

function queryCityAndWriteHTML($link)
{
	$query = 'SELECT * FROM cities ORDER BY country, state, name';
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	if ($totalRows > 0) { // Show if recordset not empty 
	  $currentRow = mysql_fetch_assoc($result);
	  do { 
			echo('<tr> ');
				//echo('<td>'); echo $currentRow['id']; echo('</td>');
				$cityId = $currentRow['id'];
				echo('<td>'); echo $currentRow['name']; echo('</td>');
				echo('<td>'); echo $currentRow['state']; echo('</td>');
				echo('<td>'); echo $currentRow['country']; echo('</td>');
				echo('<td>'); echo queryCityAgency($cityId); echo('</td>');
				//echo('<td>'); echo $currentRow['website']; echo('</td>');
				//echo('<td>'); echo $currentRow['dbname']; echo('</td>');
				$today = date("Ymd");
				$inTwoWeeks = date("Ymd", strtotime('+2 weeks'));
                                $timeStr = queryCityExpirary($cityId);
                                $timeStrToDisplay = substr($timeStr, 4, 2)."/".substr($timeStr, 6, 2)."/".substr($timeStr, 0, 4);
				if ($today>= $timeStr) {
					echo('<td> <font color="red"> <b>'); echo $timeStrToDisplay; echo('</font></b></td>');
				}
				else if ($inTwoWeeks >=  $timeStr) {
					echo('<td> <font color="blue"> <b>'); echo $timeStrToDisplay; echo('</font></b></td>');
				}
				else {
					echo('<td>'); echo $timeStrToDisplay; echo('</td>');
				}
                                $timeStr = $currentRow['lastupdate'];
                                $timeStrToDisplay = substr($timeStr, 4, 2)."/".substr($timeStr, 6, 2)."/".substr($timeStr, 0, 4);
				echo('<td>'); echo $timeStrToDisplay; echo('</td>');
                                $timeStr = $currentRow['oldbtime'];
                                $timeStrToDisplay = substr($timeStr, 4, 2)."/".substr($timeStr, 6, 2)."/".substr($timeStr, 0, 4);
				echo('<td>'); echo $timeStrToDisplay; echo('</td>');
			echo('</tr>');
		} while ($currentRow = mysql_fetch_assoc($result)); 
	} // Show if recordset not empty 	
	
	//Free resultset					
	mysql_free_result($result);
}

//Show result
echo('<table border="1">');
echo('  <tr align="center">');
//echo('     <td> <b>id</b> </td>');
echo('     <td> <b>City</b></td>');
echo('     <td> <b>State</b> </td>');
echo('     <td> <b>Country</b> </td>');
echo('     <td> <b>Agencies</b> </td>');
//echo('     <td> <b>website</b> </td>');
//echo('     <td> <b>dbname</b> </td>');
echo('     <td> <b>Valid Until</b> </td>');
echo('     <td> <b>Last Update</b> </td>');
echo('     <td> <b>Offline DB</b> </td>');
echo('  </tr>');

$dbServer='localhost';
$dbUser='root';
$dbPass='youneedpasswod';
$dbName='gtfs_info_v12';

$link = openDB($dbServer, $dbUser, $dbPass, $dbName);
queryCityAndWriteHTML($link);
//closeDB($link);

echo('</table>');
?>
