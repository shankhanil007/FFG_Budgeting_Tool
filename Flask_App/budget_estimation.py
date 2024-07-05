
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

def replace_norm_constants(sql, norm_constants):
    for key, value in norm_constants.items():
        # Use regex to find and replace the variables in the SQL
        sql = re.sub(r'\{' + key + r'\}', str(value), sql)
    return sql

def calculate_budget(city="bangalore", ward="basawanagudi_210"):
    """ function to calculate budget for a ward """

    # connect to the database
    user = os.environ.get("USER")
    password = os.environ.get("PASSWORD")
    host = os.environ.get("HOST")
    port = os.environ.get("PORT")
    database = os.environ.get("DATABASE")
    conn = psycopg2.connect(database=database, user=user, password=password, host=host, port=port) 
    
    # create a cursor 
    cur = conn.cursor() 

    # load config files
    RATE_CONFIG = load_rate_config_file(city + "_" + ward)
    SQL_CONFIG = load_sql_config_file(city + "_" + ward)

    merged_df = pd.DataFrame()

    for parent_catergory, child_catergory in six.iteritems(RATE_CONFIG):
        for child_catergory, dict in six.iteritems(RATE_CONFIG.get(parent_catergory)):
            rate = dict.get('RATE')
            norm_constants = dict.get("NORM_CONSTANTS")
            sql_template = SQL_CONFIG.get(child_catergory)
            if norm_constants:
                # Replace the constants in the SQL template
                sql_template = replace_norm_constants(sql_template, norm_constants)

            cost_calculation_sql = """  SELECT
                                            *,
                                            COALESCE(BUDGET_CALCULATION_QUANTITY::numeric, 0) * {} AS {}
                                        FROM
                                            ({}) AS SQl_QUANTITY
                                        """.format(rate, child_catergory, sql_template)
            
            final_sql_query = cost_calculation_sql
            df = pd.read_sql_query(final_sql_query, conn)
            filtered_df = df[['footpath_side', '{}'.format(child_catergory.lower())]]
            if len(merged_df) == 0:
                merged_df = filtered_df
            else:
                merged_df = pd.merge(merged_df, filtered_df, on='footpath_side', how='left')

    csv_path = "./results/cost_estimate.csv"
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    merged_df.to_csv(csv_path, index=False)
    # close the cursor and connection 
    cur.close()  
    conn.close()

if __name__ == "__main__":
    calculate_budget()