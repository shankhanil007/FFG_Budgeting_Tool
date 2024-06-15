SQL_CONFIG = dict()

SQL_CONFIG["ROAD_ID_FOOTPATH_LENGTH"] = """     SELECT
                                                    FOOTPATH_SIDE,
                                                    FOOTPATH_LENGTH
                                                FROM
                                                    {SCHEMA}.MANUAL_ENTRY   """                                                                                               


SQL_CONFIG["ROAD_ID_TRANSFORMER_ISSUE_COUNT"] = """     SELECT
                                                            ROAD_ID.FOOTPATH_SIDE,
                                                            COUNT(RITIC.FOOTPATH_SIDE) AS TRANSFORMER_ISSUE_COUNT
                                                        FROM
                                                            {SCHEMA}.ROAD_ID AS ROAD_ID
                                                            LEFT JOIN {SCHEMA}.ISSUE_POINT AS RITIC 
                                                            ON ROAD_ID.FOOTPATH_SIDE = RITIC.FOOTPATH_SIDE
                                                            AND RITIC.ISSUE_TYPE = 'B-Transformers'
                                                        GROUP BY
                                                            ROAD_ID.FOOTPATH_SIDE   """   


SQL_CONFIG["ROAD_ID_PARKING_ISSUE_LENGTH"] = """    SELECT
                                                        ROAD_ID.FOOTPATH_SIDE,
                                                        COALESCE(PARKING_ISSUE_LENGTH, 0) AS PARKING_ISSUE_LENGTH
                                                    FROM
                                                        {SCHEMA}.ROAD_ID AS ROAD_ID
                                                        LEFT JOIN (
                                                            SELECT
                                                                FOOTPATH_SIDE,
                                                                SUM(CEIL(LENGTH)) AS PARKING_ISSUE_LENGTH
                                                            FROM
                                                                {SCHEMA}.ISSUE_LINE
                                                            WHERE
                                                                ISSUE_TYPE = 'B-Encroachment by parking'
                                                            GROUP BY
                                                                FOOTPATH_SIDE
                                                        ) AS RIPIL ON ROAD_ID.FOOTPATH_SIDE = RIPIL.FOOTPATH_SIDE   """   


SQL_CONFIG["ROAD_ID_NO_PARKING_SIGNAGE_COUNT"] = """    SELECT
                                                            ROAD_ID.FOOTPATH_SIDE,
                                                            NO_PARKING_SIGNAGE_COUNT,
			                                                PARKING_ISSUE_LENGTH
                                                        FROM
                                                            {SCHEMA}.ROAD_ID AS ROAD_ID
                                                            LEFT JOIN (
                                                                SELECT
                                                                    FOOTPATH_SIDE,
                                                                    PARKING_ISSUE_LENGTH,
                                                                    CEIL((COALESCE(PARKING_ISSUE_LENGTH, 0) / {INTERVAL})) AS NO_PARKING_SIGNAGE_COUNT
                                                                FROM
                                                                    ROAD_ID_PARKING_ISSUE_LENGTH
                                                            ) AS RIPIL ON ROAD_ID.FOOTPATH_SIDE = RIPIL.FOOTPATH_SIDE   """   


SQL_CONFIG["ROAD_ID_IS_THERE_ENCROACHMENT"] = """   SELECT
                                                        FOOTPATH_SIDE,
                                                        CASE
                                                            WHEN COALESCE(RIPIL.PARKING_ISSUE_LENGTH, 0) > 0 THEN 'Y'
                                                            ELSE 'N'
                                                        END AS IS_THERE_ENCROACHMENT
                                                    FROM
                                                        ROAD_ID_PARKING_ISSUE_LENGTH AS RIPIL   """   


SQL_CONFIG["ROAD_ID_IS_PARKING_FEASIBLE"] = """     SELECT
                                                        ROAD_ID.FOOTPATH_SIDE,
                                                        COALESCE(PAQ.IS_PARKING_FEASIBLE, 'Y') AS IS_PARKING_FEASIBLE
                                                    FROM
                                                        {SCHEMA}.ROAD_ID AS ROAD_ID
                                                        LEFT JOIN {SCHEMA}.POST_AUDIT_QUESTIONS PAQ ON PAQ.FOOTPATH_SIDE = ROAD_ID.FOOTPATH_SIDE   """   


SQL_CONFIG["ROAD_ID_PARKING_REQUIRED"] = """    SELECT
                                                    RIITE.FOOTPATH_SIDE,
                                                    IS_THERE_ENCROACHMENT,
			                                        IS_PARKING_FEASIBLE,
                                                    CASE
                                                        WHEN IS_THERE_ENCROACHMENT = 'Y'
                                                        AND IS_PARKING_FEASIBLE = 'Y' THEN 'Y'
                                                        ELSE 'N'
                                                    END AS PARKING_REQUIRED
                                                FROM
                                                    ROAD_ID_IS_THERE_ENCROACHMENT RIITE
                                                    LEFT JOIN ROAD_ID_IS_PARKING_FEASIBLE AS RIIPF ON RIITE.FOOTPATH_SIDE = RIIPF.FOOTPATH_SIDE   """ 


SQL_CONFIG["ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING"] = """    SELECT
                                                                    RIPR.FOOTPATH_SIDE,
                                                                    IS_THERE_ENCROACHMENT,
                                                                    IS_PARKING_FEASIBLE,
                                                                    PARKING_REQUIRED,
                                                                    FOOTPATH_LENGTH,
                                                                    CASE
                                                                        WHEN PARKING_REQUIRED = 'Y' THEN CEIL((COALESCE(FOOTPATH_LENGTH::NUMERIC, 0) * {ROAD_SEGMENT_PERCENTAGE}))
                                                                        ELSE 0
                                                                    END AS ROAD_LENGTH_ALLOCATED_TO_PARKING
                                                                FROM
                                                                    ROAD_ID_PARKING_REQUIRED AS RIPR
                                                                    LEFT JOIN ROAD_ID_FOOTPATH_LENGTH AS RIFL ON RIPR.FOOTPATH_SIDE = RIFL.FOOTPATH_SIDE  """                   


SQL_CONFIG["ROAD_ID_PARKING_SIGNAGE_COUNT"] = """   SELECT
                                                        FOOTPATH_SIDE,
                                                        IS_THERE_ENCROACHMENT,
                                                        IS_PARKING_FEASIBLE,
                                                        PARKING_REQUIRED,
                                                        FOOTPATH_LENGTH,
                                                        ROAD_LENGTH_ALLOCATED_TO_PARKING,
                                                        CEIL(
                                                            COALESCE(ROAD_LENGTH_ALLOCATED_TO_PARKING::NUMERIC, 0) / {INTERVAL}
                                                        ) AS PARKING_SIGNAGE_COUNT
                                                    FROM
                                                        ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING  """                                                                


SQL_CONFIG["ROAD_ID_PARKING_METERS"] = """  SELECT
                                                FOOTPATH_SIDE,
                                                IS_THERE_ENCROACHMENT,
                                                IS_PARKING_FEASIBLE,
                                                PARKING_REQUIRED,
                                                FOOTPATH_LENGTH,
                                                ROAD_LENGTH_ALLOCATED_TO_PARKING,
                                                CEIL(
                                                    COALESCE(ROAD_LENGTH_ALLOCATED_TO_PARKING::NUMERIC, 0) / {INTERVAL}
                                                ) AS PARKING_METERS
                                            FROM
                                                ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING  """  


SQL_CONFIG["ROAD_ID_NUMBER_OF_TWO_WHEELERS"] = """  SELECT
                                                        FOOTPATH_SIDE,
                                                        FOOTPATH_LENGTH,
                                                        CEIL((COALESCE(FOOTPATH_LENGTH::NUMERIC, 0) * {ROAD_SEGMENT_PERCENTAGE})) AS NUMBER_OF_TWO_WHEELERS
                                                    FROM
                                                        ROAD_ID_FOOTPATH_LENGTH  """  


SQL_CONFIG["ROAD_ID_PARKING_MARKING_2W"] = """  SELECT
                                                    FOOTPATH_SIDE,
                                                    FOOTPATH_LENGTH,
			                                        NUMBER_OF_TWO_WHEELERS,
                                                    CEIL(
                                                        (
                                                            COALESCE(NUMBER_OF_TWO_WHEELERS::NUMERIC, 0) * {PERIMETER} * {LINE_THICKNESS}
                                                        )
                                                    ) AS PARKING_MARKING_2W
                                                FROM
                                                    ROAD_ID_NUMBER_OF_TWO_WHEELERS  """  


SQL_CONFIG["ROAD_ID_NUMBER_OF_FOUR_WHEELERS"] = """     SELECT
                                                            FOOTPATH_SIDE,
                                                            FOOTPATH_LENGTH,
                                                            CEIL(
                                                                (COALESCE(FOOTPATH_LENGTH::NUMERIC, 0) * {ROAD_SEGMENT_PERCENTAGE} / {UNKNOWN})
                                                            ) AS NUMBER_OF_FOUR_WHEELERS
                                                        FROM
                                                            ROAD_ID_FOOTPATH_LENGTH  """  


SQL_CONFIG["ROAD_ID_PARKING_MARKING_4W"] = """  SELECT
                                                    FOOTPATH_SIDE,
                                                    FOOTPATH_LENGTH,
	                                                NUMBER_OF_FOUR_WHEELERS,
                                                    CEIL(
                                                            (
                                                                COALESCE(NUMBER_OF_FOUR_WHEELERS::NUMERIC, 0) * {PERIMETER} * {LINE_THICKNESS}
                                                            )
                                                        ) AS PARKING_MARKING_4W
                                                FROM
                                                    ROAD_ID_NUMBER_OF_FOUR_WHEELERS  """                                                                   



