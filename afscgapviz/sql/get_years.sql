SELECT
    DISTINCT year
FROM
    availability
WHERE
    survey = ?
    AND year != 'None'
ORDER BY year