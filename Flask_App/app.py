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

base_sql = "WITH "
for k, v in six.iteritems(Query_Config["210"]):
    base_sql = base_sql + k + " AS (" + v + " ),"

base_sql = base_sql[:-1]
# sql  = sql + "select * from ROAD_ID_PARKING_MARKING_4W"

road_id = 'R3-'

for key, value in six.iteritems(Issue_Solution_Config["210"]):
	for k, v in six.iteritems(Issue_Solution_Config["210"][key]):
		sql_config = v['SQL_CONFIG']
		rate = v['RATE']
		sql = base_sql + """ select SUM({}::numeric * {}) from {} where footpath_side LIKE '%{}%'""".format(sql_config[8:], rate, sql_config, road_id)
		cur.execute(sql)
		print(k)
		print(cur.fetchall())
		print("-----------------------------------\n")

# close the cursor and connection 
cur.close() 
conn.close() 

