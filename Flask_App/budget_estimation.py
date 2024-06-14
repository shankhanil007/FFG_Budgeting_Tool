
import psycopg2 
import six
import os
import importlib
from dotenv import load_dotenv
load_dotenv()


def load_rate_config(location):
    module_name = f"configs.issue_solution_rate_configs.{location}"
    module = importlib.import_module(module_name)
    return module.RATE_CONFIG

def load_sql_config(location):
    module_name = f"configs.sql_configs.{location}"
    module = importlib.import_module(module_name)
    return module.SQL_CONFIG


def calculate_budget(database="bangalore", schema="basawanagudi_210"):
    """ function to calculate budget for a ward """

    # connect to the database
    user = os.environ.get("USER")
    password = os.environ.get("PASSWORD")
    host = os.environ.get("HOST")
    port = os.environ.get("PORT")
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port) 
    
    # create a cursor 
    cur = conn.cursor() 

    # load config files
    RATE_CONFIG = load_rate_config(database + "_" + schema)
    SQL_CONFIG = load_sql_config(database + "_" + schema)

    # create base SQL query
    base_sql = "WITH "
    for k, v in six.iteritems(SQL_CONFIG):
        base_sql = base_sql + k + " AS (" + v + " ),"
    base_sql = base_sql[:-1]
    base_sql = base_sql.format(SCHEMA=schema)

    road_id = 'R3-'

    # calculate budget estimate
    for key, value in six.iteritems(RATE_CONFIG):
        for k, v in six.iteritems(RATE_CONFIG[key]):
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


if __name__ == "__main__":
    calculate_budget()