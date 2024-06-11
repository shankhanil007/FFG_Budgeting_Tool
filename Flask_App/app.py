from flask import Flask, render_template, request, redirect, url_for 
import psycopg2 
import six
from sql_config import Query_Config

app = Flask(__name__) 

# Connect to the database 
conn = psycopg2.connect(database="", user="postgres", 
						password="", host="localhost", port="5432") 

# create a cursor 
cur = conn.cursor() 

# close the cursor and connection 
cur.close() 
conn.close() 
