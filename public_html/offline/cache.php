<?php
//=============================================================================
/// The code in this file retrieve a offline database for a city.
//
//=============================================================================

//Parse user parameter
$url = $_SERVER['REQUEST_URI'];
$processed_url = parse_url($url);
$cityId = $processed_url[ 'query' ];
header('Location:'.'http://zyao.servehttp.com:5144/ver1.3/offline/ol-'.$cityId.'.sqlite');
?>
