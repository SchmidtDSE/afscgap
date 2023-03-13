SELECT
    DISTINCT species
FROM
    availability
WHERE
    survey = ?
    AND species != 'None'
ORDER BY species