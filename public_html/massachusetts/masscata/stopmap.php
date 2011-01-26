<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN"
  "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
  <head>
    <meta http-equiv="content-type" content="text/html; charset=utf-8"/>
    <title>Stop Map</title>
    <script src="http://maps.google.com/maps?file=api&amp;v=2&amp;key=ABQIAAAA4xUoFS9qlCwHju--rlZeUhQwY-Gz4w6y5RcztTtaOvb1AYx-_RQyl9eUizShHzgdx6oPdZHTbg3ZkQ"
      type="text/javascript"></script>
    <script type="text/javascript">

    //<![CDATA[
  
	var map;
	var marker;
	var defaultCenter;
    function load() {     

		var searchString = document.location.search;
		searchString = searchString.substring(1);
		var lat = "0";
		var long = "0";
		var width = "320";
		var height = "480";
		var nvPairs = searchString.split("&");
		for (i=0; i<nvPairs.length; i++)  {
			var nvPair = nvPairs[i].split("=");
			var name = nvPair[0];
			if (name == "lat")
				lat = nvPair[1];
			else if (name == "long")
				long = nvPair[1];    
			else if (name == "width")
				width = nvPair[1];
			else if (name == "height")
				height = nvPair[1];
			}

		if (GBrowserIsCompatible()) {
			map = new GMap2(document.getElementById("map"), { size: new GSize(width,height) });
			if( (lat!= "0") && (long!= "0") ){
				var point = new GLatLng(lat, long);
				map.setCenter(point, 17);
				marker = new GMarker(point);
				map.addOverlay(marker);
			}
			else
				document.write("Parameter error! Unknow coordinate!");
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
	
    //]]>
    </script>
  </head>
  <body style="margin: 0px;" onload="load()" onunload="GUnload()" onresize="resizeDiv()">
    <div id="map" style="border: 0px solid black"></div>
  </body>
</html>