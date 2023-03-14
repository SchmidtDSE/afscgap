CREATE TABLE records (
    year INTEGER,
    survey TEXT,
    species TEXT,
    common_name TEXT,
    geohash TEXT,
    surface_temperature REAL,
    bottom_temperature REAL,
    weight REAL,
    count REAL,
    area_swept REAL,
    num_records_aggregated INTEGER
);

CREATE INDEX simplified_records_survey ON records (
    survey
);

CREATE INDEX simplified_records_year_survey_species ON records (
    year,
    survey,
    species
);

CREATE INDEX simplified_records_year_survey_common ON records (
    year,
    survey,
    common_name
);
