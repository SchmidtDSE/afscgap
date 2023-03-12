SELECT
    min(subset.min_cpue) AS min_cpue,
    max(subset.max_cpue) AS max_cpue,
    min(subset.temperature_delta) AS min_temperature,
    max(subset.temperature_delta) AS max_temperature
FROM
    (
        SELECT
            (
                CASE
                    WHEN first.cpue < second.cpue THEN first.cpue
                    ELSE second.cpue
                END
            ) AS min_cpue,
            (
                CASE
                    WHEN first.cpue > second.cpue THEN first.cpue
                    ELSE second.cpue
                END
            ) AS max_cpue,
            second.temperature - first.temperature AS temperature_delta
        FROM
            (
                SELECT
                    sum(weight) / sum(area_swept) AS cpue,
                    sum(temperature * num_records_aggregated) / sum(num_records_aggregated) AS temperature,
                    geohash AS geohash
                FROM
                    (
                        SELECT
                            %s AS temperature,
                            substr(geohash, 0, %d) AS geohash,
                            weight AS weight,
                            area_swept AS area_swept,
                            num_records_aggregated AS num_records_aggregated
                        FROM
                            records
                        WHERE
                            year = ?
                            AND survey = ?
                            AND %s = ?
                    ) firstInner
                GROUP BY
                    geohash
            ) first
        INNER JOIN
            (
                SELECT
                    sum(weight) / sum(area_swept) AS cpue,
                    sum(temperature * num_records_aggregated) / sum(num_records_aggregated) AS temperature,
                    geohash AS geohash
                FROM
                    (
                        SELECT
                            %s AS temperature,
                            substr(geohash, 0, %d) AS geohash,
                            weight AS weight,
                            area_swept AS area_swept,
                            num_records_aggregated AS num_records_aggregated
                        FROM
                            records
                        WHERE
                            year = ?
                            AND survey = ?
                            AND %s = ?
                    ) firstInner
                GROUP BY
                    geohash
            ) second
        ON
            first.geohash = second.geohash
    ) subset