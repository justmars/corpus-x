WITH statute_data AS (
    SELECT
        DATE
    FROM
        {{ statute_tbl }}
    WHERE
        id = ts.id
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
        stat_tit.statute_id = ts.id
),
codifications(codes) AS (
    SELECT
        json_group_array(
            json_object(
                'id',
                codes.id,
                'title',
                codes.title,
                'description',
                codes.description,
                'codification_date',
                codes.date
            )
        )
    FROM
        {{ code_tbl }}
        codes
    WHERE
        codes.statute_id = ts.id
)
SELECT
    ts.units,
    ts.statute_category,
    ts.statute_serial_id,
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
    ) statute_titles,
    (
        SELECT
            codes
        FROM
            codifications
    ) code_titles
FROM
    {{ statute_tbl }}
    ts
WHERE
    ts.id = '{{ target_statute_id }}'
