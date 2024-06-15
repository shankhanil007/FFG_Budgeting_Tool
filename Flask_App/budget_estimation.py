
import psycopg2 
import six
import os
import re
import importlib
import pandas as pd
from dotenv import load_dotenv
load_dotenv()

def load_rate_config_file(location):
    module_name = f"configs.issue_solution_rate_configs.{location}"
    module = importlib.import_module(module_name)
    return module.RATE_CONFIG

def load_sql_config_file(location):
    module_name = f"configs.sql_configs.{location}"
    module = importlib.import_module(module_name)
    return module.SQL_CONFIG

def replace_sql_placeholders(sql_query, constants):
    # Regular expression to find placeholders in the format {variable}
    placeholder_pattern = r'\{(\w+)\}'
    # Find all placeholders in the SQL query
    placeholders = re.findall(placeholder_pattern, sql_query)
    # Replace each placeholder with its corresponding value from norm_values
    for placeholder in placeholders:
        if placeholder != "SCHEMA":
            sql_query = sql_query.replace(f'{{{placeholder}}}', str(constants.get(placeholder)))
    return sql_query


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
    RATE_CONFIG = load_rate_config_file(database + "_" + schema)
    SQL_CONFIG = load_sql_config_file(database + "_" + schema)
    
    for parent_catergory, child_catergory in six.iteritems(RATE_CONFIG):
        for child_catergory, dict in six.iteritems(RATE_CONFIG.get(parent_catergory)):

            # create base SQL query
            processed_sql_configs = []
            base_sql = "WITH RECURSIVE "
            parent_sql_config = dict.get('SQL_CONFIG')
            rate = dict.get('RATE')
            sql_query_constants = dict.get('SQL_QUERY_CONSTANTS')

            if sql_query_constants:
                for elem in sql_query_constants:
                    # replace query placeholders with actual constants
                    sql_config = elem.get('SQL_CONFIG')
                    constants = elem.get('CONSTANTS')
                    sql_query = SQL_CONFIG.get(sql_config)
                    sql_query_replaced = replace_sql_placeholders(sql_query, constants)
                    # add with the base query
                    base_sql = base_sql + elem.get('SQL_CONFIG') + " AS (" + sql_query_replaced + " ),"
                    processed_sql_configs.append(sql_config)
        
            unprocessed_sql_configs = [key for key in SQL_CONFIG if key not in processed_sql_configs]

            for config in unprocessed_sql_configs:
                # filter out SQL queries that have placeholder constants to be replaced: SQL queries not required for the current child catergory
                placeholder_count = 0
                placeholder_pattern = r'\{(\w+)\}'
                placeholders = re.findall(placeholder_pattern, SQL_CONFIG.get(config))
                placeholder_count += sum(1 for placeholder in placeholders if placeholder != "SCHEMA")
                if placeholder_count == 0:
                    base_sql = base_sql + config + " AS (" + SQL_CONFIG.get(config) + " ),"
            # remove the last comma in base_sql
            base_sql = base_sql[:-1]
            base_sql = base_sql.format(SCHEMA=schema)       
            final_sql_query = base_sql + """ SELECT *, ({}::numeric * {}) AS COST_ESTIMATE FROM {} """.format(parent_sql_config[8:], rate, parent_sql_config)
            
            df = pd.read_sql_query(final_sql_query, conn)
            csv_path = "./results/{0}/{1}.csv".format(database + "_" + schema, child_catergory)
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            df.to_csv(csv_path, index=False)
            
    # close the cursor and connection 
    cur.close()  
    conn.close()

if __name__ == "__main__":
    calculate_budget()