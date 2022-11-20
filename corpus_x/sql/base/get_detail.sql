SELECT
    created,
    modified,
    title,
    description,
    DATE
FROM
    {{ generic_tbl }}
WHERE
    id = '{{ target_id }}'
