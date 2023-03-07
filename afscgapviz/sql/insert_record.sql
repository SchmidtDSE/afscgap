INSERT INTO records (
    year,
    survey,
    species,
    common_name,
    geohash,
    surface_temperature,
    bottom_temperature,
    weight,
    count,
    area_swept,
    num_records_aggregated
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