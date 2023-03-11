SELECT
    max(subset.cpue) AS cpue
FROM
    (
        SELECT
            weight / area_swept AS cpue
        FROM
            records
        WHERE
            year = ?
            AND survey = ?
            AND %s = ?
    ) subset