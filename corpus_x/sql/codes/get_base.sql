WITH statute_data AS (
    SELECT
        DATE
    FROM
        {{ statute_tbl }}
    WHERE
        id = tc.statute_id
),
title_list(titles) AS (
    SELECT
        json_group_array(
            json_object(
                'title',
                stat_tit.text,
                'category',
                stat_tit.category
            )
        )
    FROM
        {{ statute_title_tbl }}
        stat_tit
    WHERE
        stat_tit.statute_id = tc.statute_id
)
SELECT
    tc.units,
    tc.statute_category,
    tc.statute_serial_id,
    tc.statute_id,
    (
        SELECT
            DATE
        FROM
            statute_data
    ) statute_date,
    (
        SELECT
            titles
        FROM
            title_list
    ) statute_titles
FROM
    {{ code_tbl }}
    tc
WHERE
    tc.id = '{{ target_code_id }}'
