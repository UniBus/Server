<?php include("info.php");?>
<?php

	function queryCityExpirary($cityDBLink)
	{
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


	$currentCity = '';
	$currentState = '';
	$currentCountry = '';
	$lastUpdate = '';
	$validThrough = '';	
	$currentAgency = '';
	$gtfs_info_dbName = 'gtfs_info_v12';
	
	$link = mysql_connect("$dbServer", "$dbUser", "$dbPass") or die("Failed: Could not connect");
	mysql_select_db("$gtfs_info_dbName") or die("Failed: Could not select database");

	$query = 'SELECT * FROM cities WHERE id="'.$cityId.'"';
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	if ($totalRows > 0) { // Show if recordset not empty 
		$currentRow = mysql_fetch_assoc($result);
		$currentCity = $currentRow['name'];
		$currentState = $currentRow['state'];
		$currentCountry = $currentRow['country'];		
		$lastUpdate = $currentRow['lastupdate'];		
		$lastUpdate = date("M d, Y", mktime(0, 0, 0, substr($lastUpdate, 4, 2), substr($lastUpdate, 6, 2), substr($lastUpdate, 0, 4)));
	} // Show if recordset not empty 	
	
	//Free resultset					
	mysql_free_result($result);

	mysql_select_db("$dbName") or die("Failed: Could not select database");

	$validThrough = queryCityExpirary($link);
	$validThrough = date("M d, Y", mktime(0, 0, 0, substr($validThrough, 4, 2), substr($validThrough, 6, 2), substr($validThrough, 0, 4)));

	$query = 'SELECT * FROM agency';
	$result = mysql_query($query, $link) or die('Query failed: '. mysql_error());
	$totalRows= mysql_num_rows($result);

	if ($totalRows > 0) { // Show if recordset not empty 
		$currentRow = mysql_fetch_assoc($result);
		do { 
			if ($currentAgency == '')
				$currentAgency = $currentRow['agency_name'];
			else
				$currentAgency = $currentAgency .', '. $currentRow['agency_name'];
		} while ($currentRow = mysql_fetch_assoc($result)); 
	} // Show if recordset not empty 	
	
	//Free resultset					
	mysql_free_result($result);
	
?>
<!DOCTYPE HTML PUBLIC "-//IETF//DTD HTML 2.0//EN">
<html>
<head>
	<STYLE TYPE="text/css">
	<!--
	.indented
	   {
	   padding-left: 20pt;
	   padding-right: 10pt;
	   }
	-->
	</STYLE>
</head>
<body>
	<h3>City</h3>
	<p CLASS="indented">
		<?php echo($currentCity.', '.$currentState.', '.$currentCountry); ?>.
	</p>
	
	<h3>Agency</h3>
	<p CLASS="indented">
		<?php echo($currentAgency); ?>.
	</p>
	
	<h3>Last update</h3>
	<p CLASS="indented">
		<?php echo($lastUpdate); ?>
	</p>
	
	<h3>Valid through</h3>
	<p CLASS="indented">
		<?php echo($validThrough); ?>
	</p>
	
</body>

</html>
