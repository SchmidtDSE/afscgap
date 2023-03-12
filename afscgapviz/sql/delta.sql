SELECT
    second.year - first.year AS year,
    first.survey AS survey,
    second.species || "-" || first.species AS species,
    second.common_name || "-" || first.common_name AS common_name,
    first.geohash AS geohash,
    second.surface_temperature - first.surface_temperature AS surface_temperature,
    second.bottom_temperature - first.bottom_temperature AS bottom_temperature,
    second.weight - first.weight AS weight,
    second.count - first.count AS count,
    second.area_swept - first.area_swept AS area_swept,
    first.num_records_aggregated + second.num_records_aggregated AS num_records_aggregated
FROM
    (
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
    ) first
INNER JOIN
    (
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
    ) second
ON
    first.geohash = second.geohash
    AND first.survey = second.survey