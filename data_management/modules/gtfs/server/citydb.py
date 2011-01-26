#! /usr/bin/python
## This module creates a mySQL database
# 
# It take one parameter, as
#
#	   create_db $dbName
#
import csv
import MySQLdb
import sys
import string
import os

def create_db(dbhost, dbuser, dbpass, dbname):
	print "Create a MySQL database."
	
	try:
		#create database if it doesn't exist
		print "   [*] Connecting to databae server." 
		conn = MySQLdb.connect(host = dbhost,
							   user = dbuser,
							   passwd = dbpass)
		cursor = conn.cursor()
	
		print "   [*] Createing databae %s." %dbname
		cursor.execute("""CREATE DATABASE IF NOT EXISTS """ + dbname)
		conn.commit()
		conn.close()
		print "   [*] Databae created." 
		print "   [*] Done \n"
		
	except MySQLdb.Error, e:
		print "Error %d %s\n" % (e.args[0], e.args[1])
		sys.exit(1)

def drop_db(dbname):
	print "Delete a MySQL database."
	
	try:
		#create database if it doesn't exist
		print "   [*] Connecting to databae server." 
		conn = MySQLdb.connect(host = dbhost,
							   user = dbuser,
							   passwd = dbpass)
		cursor = conn.cursor()
		print "   [*] Deleteing databae %s." %dbname
		cursor.execute("""DROP DATABASE IF EXISTS """ + dbname)
		conn.commit()
		conn.close()	
		print "   [*] Databae deleted." 
		print "   [*] Done \n"
		
	except MySQLdb.Error, e:
		print "Error %d %s\n" % (e.args[0], e.args[1])
		sys.exit(1)

def create(dbhost, dbuser, dbpass, dbname):
	create_db(dbhost, dbuser, dbpass, dbname)

def drop(dbname):
	drop_db(dbhost, dbuser, dbpass, dbname)
