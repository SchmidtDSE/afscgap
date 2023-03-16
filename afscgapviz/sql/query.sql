SELECT
    individual.year AS year,
    individual.survey AS survey,
    individual.species AS species,
    individual.common_name AS common_name,
    individual.geohash AS geohash,
    sum(individual.surface_temperature * individual.num_records_aggregated) / sum(individual.num_records_aggregated) AS surface_temperature,
    sum(individual.bottom_temperature * individual.num_records_aggregated) / sum(individual.num_records_aggregated) AS bottom_temperature,
    sum(weight) AS weight,
    sum(count) AS count,
    sum(area_swept) AS area_swept,
    sum(num_records_aggregated) AS num_records_aggregated
FROM
    (
        SELECT
            year,
            survey,
            species,
            common_name,
            substr(geohash, 0, %d) AS geohash,
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
    ) individual
GROUP BY
    individual.year,
    individual.survey,
    individual.species,
    individual.common_name,
    individual.geohash
