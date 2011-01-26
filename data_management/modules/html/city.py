#! /usr/bin/python
## This module creates/updates query for city
#    
# <?php  
#   $timeZone = 2; 
#   $queryPeriod = 12;
#   $dbServer='localhost';
#   $cityId='austin';
#   $dbUser='root';
#   $dbPass='awang';
#   $dbName='bus_austin';
#   $cityName='Austin';
#   $agencyName='capmetro';
# ?>
#

import sys
import string
import os
import shutil

def copy_template(directory):
	os.rmdir(directory)
	templateDir = os.path.join(os.path.dirname( os.path.realpath( __file__ ) ), 'template')
	shutil.copytree(templateDir, directory)
	

def new_city(cityIdentifier, directory):

	copy_template(directory)

	timeZone = 0
	queryPeriod = 12
	cityId = cityIdentifier
	dbServer = 'localhost'
	dbUser = 'unibus13'
	dbPass = 'unibus1.3'
	dbName = 'bus_%s'%cityIdentifier
	cityName = cityIdentifier
	agencyName = ''

	userInput = raw_input('Time difference [ %d]:'%timeZone);
	if userInput != '':
		timeZone = userInput

	userInput = raw_input('Query period    [ %d]:'%queryPeriod);
	if userInput != '':
		queryPeriod = userInput

	userInput = raw_input('City name       [ %s]:'%cityId);
	if userInput != '':
		cityName = userInput

	userInput = raw_input('MySQl DB name   [ %s]:'%dbServer);
	if userInput != '':
		dbServer = userInput

	userInput = raw_input('DB server name  [ %s]:'%dbName);
	if userInput != '':
		dbName = userInput
	     
	userInput = raw_input('DB user name    [ %s]:'%dbUser);
	if userInput != '':
		dbUser = userInput
	      
	userInput = raw_input('DB user passwrd [ %s]:'%dbPass);
	if userInput != '':
		dbPass = userInput

	userInput = raw_input('Agency name     [ %s]:'%agencyName);
	if userInput != '':
		agencyName = userInput

	infoFileName = os.path.join(directory, "info.php")

	info = open(infoFileName, "w")
	info.writelines("<?php\n")
	info.writelines("   $timeZone = %d;\n"%timeZone)
	info.writelines("   $queryPeriod = %d;\n"%queryPeriod)
	info.writelines("   $dbServer = '%s';\n"%dbServer)
	info.writelines("   $cityId = '%s';\n"%cityId)
	info.writelines("   $dbUser = '%s';\n"%dbUser)
	info.writelines("   $dbPass = '%s';\n"%dbPass)
	info.writelines("   $dbName = '%s';\n"%dbName)
	info.writelines("   $cityName = '%s';\n"%cityName)
	info.writelines("   $agencyName = '%s';\n"%agencyName)
	info.writelines("?>")

	info.close();

def create(cityIdentifier, directory):
	new_city(cityIdentifier, directory)

