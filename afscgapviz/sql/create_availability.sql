CREATE TABLE availability AS
SELECT
    year,
    species,
    common_name,
    survey,
    count(1) AS cnt
FROM
    records
GROUP BY
    year,
    species,
    common_name,
    survey;

CREATE INDEX availability_survey ON availability(survey);
