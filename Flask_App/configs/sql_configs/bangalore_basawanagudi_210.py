SQL_CONFIG = dict()

SQL_CONFIG["COMPACT_TRANSFORMER"] = """ SELECT
                                            ROAD_ID.FOOTPATH_SIDE,
                                            COUNT(RITIC.FOOTPATH_SIDE) AS BUDGET_CALCULATION_QUANTITY
                                        FROM
                                            footpath_audit.ROAD_ID AS ROAD_ID
                                            LEFT JOIN footpath_audit.ISSUE_POINT AS RITIC ON ROAD_ID.FOOTPATH_SIDE = RITIC.FOOTPATH_SIDE
                                            AND RITIC.ISSUE_TYPE = 'B-Transformers'
                                        GROUP BY
                                            ROAD_ID.FOOTPATH_SIDE """   

SQL_CONFIG["PARKING_SIGNAGE"] = """ WITH
                                        ROAD_ID_PARKING_ISSUE_LENGTH AS (
                                            SELECT
                                                ROAD_ID.FOOTPATH_SIDE,
                                                COALESCE(PARKING_ISSUE_LENGTH, 0) AS PARKING_ISSUE_LENGTH
                                            FROM
                                                footpath_audit.ROAD_ID AS ROAD_ID
                                                LEFT JOIN (
                                                    SELECT
                                                        FOOTPATH_SIDE,
                                                        SUM(CEIL(LENGTH)) AS PARKING_ISSUE_LENGTH
                                                    FROM
                                                        footpath_audit.ISSUE_LINE
                                                    WHERE
                                                        ISSUE_TYPE = 'B-Encroachment by parking'
                                                    GROUP BY
                                                        FOOTPATH_SIDE
                                                ) AS RIPIL ON ROAD_ID.FOOTPATH_SIDE = RIPIL.FOOTPATH_SIDE
                                        ),
                                        ROAD_ID_IS_THERE_ENCROACHMENT AS (
                                            SELECT
                                                *,
                                                CASE
                                                    WHEN COALESCE(RIPIL.PARKING_ISSUE_LENGTH, 0) > 0 THEN 'Y'
                                                    ELSE 'N'
                                                END AS IS_THERE_ENCROACHMENT
                                            FROM
                                                ROAD_ID_PARKING_ISSUE_LENGTH AS RIPIL
                                        ),
                                        ROAD_ID_IS_PARKING_FEASIBLE AS (
                                            SELECT
                                                FOOTPATH_SIDE,
                                                IS_PARKING_FEASIBLE
                                            FROM
                                                footpath_audit.POST_AUDIT_QUESTIONS PAQ
                                        ),
                                        ROAD_ID_PARKING_REQUIRED AS (
                                            SELECT
                                                RIITE.*,
                                                RIIPF.IS_PARKING_FEASIBLE,
                                                CASE
                                                    WHEN IS_THERE_ENCROACHMENT = 'Y'
                                                    AND IS_PARKING_FEASIBLE = 'Y' THEN 'Y'
                                                    ELSE 'N'
                                                END AS PARKING_REQUIRED
                                            FROM
                                                ROAD_ID_IS_THERE_ENCROACHMENT RIITE
                                                LEFT JOIN ROAD_ID_IS_PARKING_FEASIBLE AS RIIPF ON RIITE.FOOTPATH_SIDE = RIIPF.FOOTPATH_SIDE
                                        ),
                                        ROAD_ID_FOOTPATH_LENGTH AS (
                                            SELECT
                                                FOOTPATH_SIDE,
                                                FOOTPATH_LENGTH
                                            FROM
                                                footpath_audit.MANUAL_ENTRY
                                        ),
                                        ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING AS (
                                            SELECT
                                                RIPR.*,
                                                RIFL.FOOTPATH_LENGTH,
                                                CASE
                                                    WHEN PARKING_REQUIRED = 'Y' THEN CEIL((COALESCE(FOOTPATH_LENGTH::NUMERIC, 0) * {ROAD_SEGMENT_PERCENTAGE}))
                                                    ELSE 0
                                                END AS ROAD_LENGTH_ALLOCATED_TO_PARKING
                                            FROM
                                                ROAD_ID_PARKING_REQUIRED AS RIPR
                                                LEFT JOIN ROAD_ID_FOOTPATH_LENGTH AS RIFL ON RIPR.FOOTPATH_SIDE = RIFL.FOOTPATH_SIDE
                                        ),
                                        ROAD_ID_PARKING_SIGNAGE_COUNT AS (
                                            SELECT
                                                *,
                                                CEIL(
                                                    COALESCE(ROAD_LENGTH_ALLOCATED_TO_PARKING::NUMERIC, 0) / {INTERVAL}
                                                ) AS BUDGET_CALCULATION_QUANTITY
                                            FROM
                                                ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING
                                        )
                                    SELECT
                                        *
                                    FROM
                                        ROAD_ID_PARKING_SIGNAGE_COUNT """ 


SQL_CONFIG["PARKING_METERS"] = """  WITH
                                        ROAD_ID_PARKING_ISSUE_LENGTH AS (
                                            SELECT
                                                ROAD_ID.FOOTPATH_SIDE,
                                                COALESCE(PARKING_ISSUE_LENGTH, 0) AS PARKING_ISSUE_LENGTH
                                            FROM
                                                footpath_audit.ROAD_ID AS ROAD_ID
                                                LEFT JOIN (
                                                    SELECT
                                                        FOOTPATH_SIDE,
                                                        SUM(CEIL(LENGTH)) AS PARKING_ISSUE_LENGTH
                                                    FROM
                                                        footpath_audit.ISSUE_LINE
                                                    WHERE
                                                        ISSUE_TYPE = 'B-Encroachment by parking'
                                                    GROUP BY
                                                        FOOTPATH_SIDE
                                                ) AS RIPIL ON ROAD_ID.FOOTPATH_SIDE = RIPIL.FOOTPATH_SIDE
                                        ),
                                        ROAD_ID_IS_THERE_ENCROACHMENT AS (
                                            SELECT
                                                *,
                                                CASE
                                                    WHEN COALESCE(RIPIL.PARKING_ISSUE_LENGTH, 0) > 0 THEN 'Y'
                                                    ELSE 'N'
                                                END AS IS_THERE_ENCROACHMENT
                                            FROM
                                                ROAD_ID_PARKING_ISSUE_LENGTH AS RIPIL
                                        ),
                                        ROAD_ID_IS_PARKING_FEASIBLE AS (
                                            SELECT
                                                FOOTPATH_SIDE,
                                                IS_PARKING_FEASIBLE
                                            FROM
                                                footpath_audit.POST_AUDIT_QUESTIONS PAQ
                                        ),
                                        ROAD_ID_PARKING_REQUIRED AS (
                                            SELECT
                                                RIITE.*,
                                                RIIPF.IS_PARKING_FEASIBLE,
                                                CASE
                                                    WHEN IS_THERE_ENCROACHMENT = 'Y'
                                                    AND IS_PARKING_FEASIBLE = 'Y' THEN 'Y'
                                                    ELSE 'N'
                                                END AS PARKING_REQUIRED
                                            FROM
                                                ROAD_ID_IS_THERE_ENCROACHMENT RIITE
                                                LEFT JOIN ROAD_ID_IS_PARKING_FEASIBLE AS RIIPF ON RIITE.FOOTPATH_SIDE = RIIPF.FOOTPATH_SIDE
                                        ),
                                        ROAD_ID_FOOTPATH_LENGTH AS (
                                            SELECT
                                                FOOTPATH_SIDE,
                                                FOOTPATH_LENGTH
                                            FROM
                                                footpath_audit.MANUAL_ENTRY
                                        ),
                                        ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING AS (
                                            SELECT
                                                RIPR.*,
                                                RIFL.FOOTPATH_LENGTH,
                                                CASE
                                                    WHEN PARKING_REQUIRED = 'Y' THEN CEIL((COALESCE(FOOTPATH_LENGTH::NUMERIC, 0) * {ROAD_SEGMENT_PERCENTAGE}))
                                                    ELSE 0
                                                END AS ROAD_LENGTH_ALLOCATED_TO_PARKING
                                            FROM
                                                ROAD_ID_PARKING_REQUIRED AS RIPR
                                                LEFT JOIN ROAD_ID_FOOTPATH_LENGTH AS RIFL ON RIPR.FOOTPATH_SIDE = RIFL.FOOTPATH_SIDE
                                        ),
                                        ROAD_ID_PARKING_METERS AS (
                                            SELECT
                                                *,
                                                CEIL(
                                                    COALESCE(ROAD_LENGTH_ALLOCATED_TO_PARKING::NUMERIC, 0) / {INTERVAL}
                                                ) AS BUDGET_CALCULATION_QUANTITY
                                            FROM
                                                ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING
                                        )
                                    SELECT
                                        *
                                    FROM
                                        ROAD_ID_PARKING_METERS """  