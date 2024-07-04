
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

            if parent_sql_config == "ROAD_ID_PARKING_MARKING_2W":
                print(base_sql)

            cost_calculation_sql = """  SELECT
                                            CAST(
                                                REGEXP_REPLACE(FOOTPATH_SIDE, '[^0-9]', '', 'g') AS INTEGER
                                            ) AS NUMERIC_PART,
                                            SUBSTRING(FOOTPATH_SIDE FROM '[^-]*$') AS ALPHABETIC_PART,
                                            *,
                                            ({}::numeric * {}) AS COST_ESTIMATE
                                        FROM
                                            {}
                                        ORDER BY
                                            NUMERIC_PART,
                                            ALPHABETIC_PART """.format(parent_sql_config[8:], rate, parent_sql_config)
            
            final_sql_query = base_sql + cost_calculation_sql
            csv_path = "./results/{0}/{1}.csv".format(database + "_" + schema, child_catergory)
            os.makedirs(os.path.dirname(csv_path), exist_ok=True)
            df = pd.read_sql_query(final_sql_query, conn)
            df.to_csv(csv_path, index=False)

    # close the cursor and connection 
    cur.close()  
    conn.close()



def calculate_budget_new(database="bangalore", schema="basawanagudi_110"):
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