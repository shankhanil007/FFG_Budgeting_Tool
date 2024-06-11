

Query_Config = dict()

Query_Config["210"] = dict()

# Query_Config["210"]["ROAD_ID_WITH_LANDUSE"] = """   SELECT
#                                                         FOOTPATH_SIDE,
#                                                         LANDUSE
#                                                     FROM
#                                                         (
#                                                             SELECT
#                                                                 FOOTPATH_SIDE,
#                                                                 LANDUSE,
#                                                                 TYPE_COUNT,
#                                                                 ROW_NUMBER() OVER (
#                                                                     PARTITION BY
#                                                                         FOOTPATH_SIDE
#                                                                     ORDER BY
#                                                                         TYPE_COUNT DESC,
#                                                                         LANDUSE
#                                                                 ) AS RN
#                                                             FROM
#                                                                 (
#                                                                     SELECT
#                                                                         FOOTPATH_SIDE,
#                                                                         LANDUSE,
#                                                                         COUNT(*) AS TYPE_COUNT
#                                                                     FROM
#                                                                         TESTDB1.PROFILE_DATA.PROFILE_DATA
#                                                                     GROUP BY
#                                                                         FOOTPATH_SIDE,
#                                                                         LANDUSE
#                                                                 ) AS SUB_QUERY_1
#                                                         ) AS SUB_QUERY_2
#                                                     WHERE
#                                                         RN = 1  """




# Query_Config["210"]["ROAD_ID_WITH_AVG_WIDTH_HEIGHT"] = """  SELECT
#                                                                 road_id.FOOTPATH_SIDE,
#                                                                 FOOTPATH_WIDTH,
#                                                                 FOOTPATH_HEIGHT
#                                                             FROM
#                                                                 TESTDB1.ROAD_ID.ROAD_ID AS road_id
#                                                             LEFT JOIN (
#                                                                 SELECT
#                                                                     FOOTPATH_SIDE,
#                                                                     ROUND(AVG(FOOTPATH_WIDTH)::NUMERIC, 1) AS FOOTPATH_WIDTH,
#                                                                     ROUND(AVG(FOOTPATH_HEIGHT)::NUMERIC, 1) AS FOOTPATH_HEIGHT
#                                                                 FROM
#                                                                     TESTDB1.PROFILE_DATA.PROFILE_DATA
#                                                                 GROUP BY
#                                                                     FOOTPATH_SIDE
#                                                             ) AS RIAWH ON road_id.FOOTPATH_SIDE = RIAWH.FOOTPATH_SIDE   """         


Query_Config["210"]["ROAD_ID_FOOTPATH_LENGTH"] = """   SELECT
                                                                FOOTPATH_SIDE,
                                                                FOOTPATH_LENGTH
                                                            FROM
                                                                TESTDB1.MANUAL_ENTRY.MANUAL_ENTRY   """                                                                                               

Query_Config["210"]["ROAD_ID_TRANSFORMER_COUNT"] = """  SELECT
                                                            ROAD_ID.FOOTPATH_SIDE,
                                                            COUNT(RITC.FOOTPATH_SIDE) AS TRANSFORMER_ISSUE_COUNT
                                                        FROM
                                                            TESTDB1.ROAD_ID.ROAD_ID AS ROAD_ID
                                                            LEFT JOIN TESTDB1.ISSUE_POINT.ISSUE_POINT AS RITC 
                                                            ON ROAD_ID.FOOTPATH_SIDE = RITC.FOOTPATH_SIDE
                                                            AND RITC.ISSUE_TYPE = 'B-Transformers'
                                                        GROUP BY
                                                            ROAD_ID.FOOTPATH_SIDE
                                                        """   

Query_Config["210"]["ROAD_ID_PARKING_ISSUE_LENGTH"] = """   SELECT
                                                                ROAD_ID.FOOTPATH_SIDE,
                                                                COALESCE(PARKING_ISSUE_LENGTH, 0) AS PARKING_ISSUE_LENGTH
                                                            FROM
                                                                TESTDB1.ROAD_ID.ROAD_ID AS ROAD_ID
                                                                LEFT JOIN (
                                                                    SELECT
                                                                        FOOTPATH_SIDE,
                                                                        SUM(CEIL(LENGTH)) AS PARKING_ISSUE_LENGTH
                                                                    FROM
                                                                        TESTDB1.ISSUE_LINE.ISSUE_LINE
                                                                    WHERE
                                                                        ISSUE_TYPE = 'B-Encroachment by parking'
                                                                    GROUP BY
                                                                        FOOTPATH_SIDE
                                                                ) AS PIL ON ROAD_ID.FOOTPATH_SIDE = PIL.FOOTPATH_SIDE   """   


Query_Config["210"]["ROAD_ID_NO_PARKING_SIGNAGE_COUNT"] = """   SELECT
                                                                    ROAD_ID.FOOTPATH_SIDE,
                                                                    RIPIL.NO_PARKING_SIGNAGE_COUNT
                                                                FROM
                                                                    TESTDB1.ROAD_ID.ROAD_ID AS ROAD_ID
                                                                    LEFT JOIN (
                                                                        SELECT
                                                                            FOOTPATH_SIDE,
                                                                            CEIL((COALESCE(PARKING_ISSUE_LENGTH, 0) / 50.0)) AS NO_PARKING_SIGNAGE_COUNT
                                                                        FROM
                                                                            ROAD_ID_PARKING_ISSUE_LENGTH
                                                                    ) AS RIPIL ON ROAD_ID.FOOTPATH_SIDE = RIPIL.FOOTPATH_SIDE   """   


Query_Config["210"]["ROAD_ID_IS_THERE_ENCROACHMENT"] = """  SELECT
                                                                FOOTPATH_SIDE,
                                                                CASE
                                                                    WHEN COALESCE(RIPIL.PARKING_ISSUE_LENGTH, 0) > 0 THEN 'Y'
                                                                    ELSE 'N'
                                                                END AS IS_THERE_ENCROACHMENT
                                                            FROM
                                                                ROAD_ID_PARKING_ISSUE_LENGTH AS RIPIL   """   


Query_Config["210"]["ROAD_ID_IS_PARKING_FEASIBLE"] = """    SELECT
                                                                ROAD_ID.FOOTPATH_SIDE,
                                                                COALESCE(PAQ.IS_PARKING_FEASIBLE, 'Y') AS IS_PARKING_FEASIBLE
                                                            FROM
                                                                TESTDB1.ROAD_ID.ROAD_ID AS ROAD_ID
                                                                LEFT JOIN TESTDB1.POST_AUDIT_QUESTIONS.POST_AUDIT_QUESTIONS PAQ ON PAQ.FOOTPATH_SIDE = ROAD_ID.FOOTPATH_SIDE   """   


Query_Config["210"]["ROAD_ID_PARKING_REQUIRED"] = """   SELECT
                                                            RIITE.FOOTPATH_SIDE,
                                                            CASE
                                                                WHEN IS_THERE_ENCROACHMENT = 'Y'
                                                                AND IS_PARKING_FEASIBLE = 'Y' THEN 'Y'
                                                                ELSE 'N'
                                                            END AS PARKING_REQUIRED
                                                        FROM
                                                            ROAD_ID_IS_THERE_ENCROACHMENT RIITE
                                                            LEFT JOIN ROAD_ID_IS_PARKING_FEASIBLE AS RIIPF ON RIITE.FOOTPATH_SIDE = RIIPF.FOOTPATH_SIDE   """ 


Query_Config["210"]["ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING"] = """   SELECT
                                                                            RIPR.FOOTPATH_SIDE,
                                                                            CASE
                                                                                WHEN PARKING_REQUIRED = 'Y' THEN CEIL((COALESCE(FOOTPATH_LENGTH::NUMERIC, 0) * 0.3))
                                                                                ELSE 0
                                                                            END AS ROAD_LENGTH_ALLOCATED_TO_PARKING
                                                                        FROM
                                                                            ROAD_ID_PARKING_REQUIRED AS RIPR
                                                                            LEFT JOIN ROAD_ID_FOOTPATH_LENGTH AS RIFL ON RIPR.FOOTPATH_SIDE = RIFL.FOOTPATH_SIDE  """                   


Query_Config["210"]["ROAD_ID_PARKING_SIGNAGE"] = """    SELECT
                                                            FOOTPATH_SIDE,
                                                            CEIL(
                                                                COALESCE(ROAD_LENGTH_ALLOCATED_TO_PARKING::NUMERIC, 0) / 50.0
                                                            ) AS PARKING_SIGNAGE
                                                        FROM
                                                            ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING  """                                                                


Query_Config["210"]["ROAD_ID_PARKING_METERS"] = """ SELECT
                                                        FOOTPATH_SIDE,
                                                        CEIL(
                                                            COALESCE(ROAD_LENGTH_ALLOCATED_TO_PARKING::NUMERIC, 0) / 150.0
                                                        ) AS PARKING_METERS
                                                    FROM
                                                        ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING  """  


Query_Config["210"]["ROAD_ID_NUMBER_OF_TWO_WHEELERS"] = """ SELECT
                                                        FOOTPATH_SIDE,
                                                        CEIL(
                                                            COALESCE(ROAD_LENGTH_ALLOCATED_TO_PARKING::NUMERIC, 0) / 150.0
                                                        ) AS PARKING_METERS
                                                    FROM
                                                        ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING  """  






