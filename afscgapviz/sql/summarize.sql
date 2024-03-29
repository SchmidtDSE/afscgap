SELECT
    min(subset.cpue) AS min_cpue,
    max(subset.cpue) AS max_cpue,
    min(subset.temperature) AS min_temperature,
    max(subset.temperature) AS max_temperature,
    sum(weight) / sum(area_swept) AS first_cpue,
    -1 AS second_cpue
FROM
    (
        SELECT
            sum(weight) / sum(area_swept) AS cpue,
            sum(weight) AS weight,
            sum(area_swept) AS area_swept,
            sum(%s * num_records_aggregated) / sum(num_records_aggregated) AS temperature
        FROM
            records
        WHERE
            year = ?
            AND survey = ?
            AND %s = ?
        GROUP BY
            substr(geohash, 0, %d)
    ) subset
    