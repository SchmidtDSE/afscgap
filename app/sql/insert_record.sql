INSERT INTO simplified_records (
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
) VALUES (
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?,
    ?
);