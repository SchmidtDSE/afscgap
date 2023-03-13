SELECT
    DISTINCT common_name
FROM
    availability
WHERE
    survey = ?
    AND common_name != 'None'
ORDER BY common_name