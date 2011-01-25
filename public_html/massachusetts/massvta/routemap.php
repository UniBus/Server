<?php include("shapes.php");?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"  
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
	<meta http-equiv="content-type" content="text/html; charset=utf-8"/>
	<title>Route Map</title>
	<script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAA4xUoFS9qlCwHju--rlZeUhQwY-Gz4w6y5RcztTtaOvb1AYx-_RQyl9eUizShHzgdx6oPdZHTbg3ZkQ"
			type="text/javascript"></script>
	<script type="text/javascript">
	
	var map;
	var defaultCenter;
	function initialize() {
		if (GBrowserIsCompatible()) {
			map = new GMap2(document.getElementById("map"), { size: new GSize(320,480) });

			var numOfPts = <?php echo count($shape_pt_lats)?>;
			var showConnections = <?php echo $connections?>;
		
			var points = [];		
			<?php 
				$count = count($shape_pt_lats);
				for ($i=0; $i<$count; $i++) { 
					echo "points.push(new GLatLng(".$shape_pt_lats[$i].",".$shape_pt_lons[$i]."));\n\t\t\t";
				}
			?>

			<?php echo "var bounds = new GLatLngBounds(new GLatLng(". $min_lat. ",". $min_lon. "), new GLatLng (". $max_lat. ",". $max_lon ."));\n"?>			
			var zoomLevel = map.getBoundsZoomLevel(bounds);
			map.setCenter(bounds.getCenter(), zoomLevel);
			defaultCenter = bounds.getCenter();

			if (showConnections){
				var polyline = new GPolyline(points, "#0000ff", 10);
				map.addOverlay(polyline);
	
				if (numOfPts > 0){			
					var markerStart = new GMarker(points[0]);
					var markerGoal = new GMarker(points[numOfPts-1]);
					map.addOverlay(markerStart);
					map.addOverlay(markerGoal);
				}
			}
			else {
				for (i=0; i<numOfPts; i++){
					map.addOverlay(new GMarker(points[i]));
				}
			}

		}
	} 
	
	function resizeDiv() {
		var mapEl = document.getElementById("map");
		mapEl.style.width = (window.innerWidth - 0) + 'px';
		mapEl.style.height = (window.innerHeight - 0) + 'px';
	}
	
	function resetCenter() {
		var zoomLevel = map.getZoom();
		map.setCenter(defaultCenter, zoomLevel);		
	}

	</script>
  </head>
  <body style="margin: 0px;" onload="initialize()" onunload="GUnload()" onresize="resizeDiv()">
	<div id="map" style="border: 0px; width: 320px; height: 480px"></div>
  </body>
</html>