
RATE_CONFIG = dict()

RATE_CONFIG["STREET_INFRASTRUCTURE"] = dict()

RATE_CONFIG["STREET_INFRASTRUCTURE"]["COMPACT_TRANSFORMER"] = {
    "SQL_CONFIG": "ROAD_ID_TRANSFORMER_ISSUE_COUNT",
    "RATE": 65000.00
}

RATE_CONFIG["SIGNAGE"] = dict()

RATE_CONFIG["SIGNAGE"]["PARKING_SIGNAGE"] = {
    "SQL_CONFIG": "ROAD_ID_PARKING_SIGNAGE_COUNT",
    "RATE": 3309.32,
    "SQL_QUERY_CONSTANTS": [{
        "SQL_CONFIG": "ROAD_ID_PARKING_SIGNAGE_COUNT",
        "CONSTANTS" : { "INTERVAL": 50.0 }, 
    },{
        "SQL_CONFIG": "ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING",
        "CONSTANTS" : { "ROAD_SEGMENT_PERCENTAGE": 0.3 }, 
    }], 
}


RATE_CONFIG["PARKING"] = dict()

RATE_CONFIG["PARKING"]["PARKING_METERS"] = {
    "SQL_CONFIG": "ROAD_ID_PARKING_METERS",
    "RATE": 20000.00,
    "SQL_QUERY_CONSTANTS": [{
        "SQL_CONFIG": "ROAD_ID_PARKING_METERS",
        "CONSTANTS" : { "INTERVAL": 150.0 }, 
    },{
        "SQL_CONFIG": "ROAD_ID_ROAD_LENGTH_ALLOCATED_TO_PARKING",
        "CONSTANTS" : { "ROAD_SEGMENT_PERCENTAGE": 0.3 }, 
    }], 
}

RATE_CONFIG["PARKING"]["PARKING_MARKING_2W"] = {
    "SQL_CONFIG": "ROAD_ID_PARKING_MARKING_2W",
    "RATE": 454.74,
    "SQL_QUERY_CONSTANTS": [{
        "SQL_CONFIG": "ROAD_ID_PARKING_MARKING_2W",
        "CONSTANTS" : { "PERIMETER": 4, "LINE_THICKNESS": 0.15 },
    },{
        "SQL_CONFIG": "ROAD_ID_NUMBER_OF_TWO_WHEELERS",
        "CONSTANTS" : { "ROAD_SEGMENT_PERCENTAGE": 0.15 }, 
    }], 
}

RATE_CONFIG["PARKING"]["PARKING_MARKING_4W"] = {
    "SQL_CONFIG": "ROAD_ID_PARKING_MARKING_4W",
    "RATE": 454.74,
    "SQL_QUERY_CONSTANTS": [{
        "SQL_CONFIG": "ROAD_ID_PARKING_MARKING_4W",
        "CONSTANTS" : { "PERIMETER": 7, "LINE_THICKNESS": 0.15 }, 
    },{
        "SQL_CONFIG": "ROAD_ID_NUMBER_OF_FOUR_WHEELERS",
        "CONSTANTS" : { "ROAD_SEGMENT_PERCENTAGE": 0.15, "UNKNOWN": 5 }, 
    }], 
}

RATE_CONFIG["PARKING"]["NO_PARKING_SIGNAGE"] = {
    "SQL_CONFIG": "ROAD_ID_NO_PARKING_SIGNAGE_COUNT",
    "RATE": 3309.32,
    "SQL_QUERY_CONSTANTS": [{
        "SQL_CONFIG": "ROAD_ID_NO_PARKING_SIGNAGE_COUNT",
        "CONSTANTS" : { "INTERVAL": 50.0 }, 
    }], 
}