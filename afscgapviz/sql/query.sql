SELECT
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
FROM
    records
WHERE
    year = ?
    AND survey = ?
    AND %s = ?
