CREATE TABLE simplified_records (
    year: INTEGER,
    survey: TEXT,
    species: TEXT,
    common_name: TEXT,
    geohash: TEXT,
    surface_temperature: REAL,
    bottom_temperature: REAL,
    weight: REAL,
    count: REAL,
    area_swept: REAL,
    num_records_aggregated: INTEGER
);

CREATE INDEX simplified_records_year_geohash_species ON simplified_records (
    year,
    geohash,
    species
);

CREATE INDEX simplified_records_year_geohash_common ON simplified_records (
    year,
    geohash,
    common_name
);
