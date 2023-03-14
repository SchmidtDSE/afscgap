SELECT
    DISTINCT year
FROM
    availability
WHERE
    survey = ?
ORDER BY year