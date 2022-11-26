WITH raw_statute_pairs(
    cat,
    idx
) AS (
    -- get the category and serial ids from the statute references table
    SELECT
        r.statute_category,
        r.statute_serial_id
    FROM
        {{ ref_tbl }}
        r
    WHERE
        r.statute_id = '{{ affecting_statute_id }}'
),
ordered_statutes AS (
    -- sort the ids and extract the fields from the statutes table
    SELECT
        id,
        title,
        description,
        DATE
    FROM
        {{ statute_tbl }}
        s
        JOIN raw_statute_pairs rr
        ON s.statute_category = rr.cat
        AND s.statute_serial_id = rr.idx
    GROUP BY
        id
    ORDER BY
        DATE DESC
)
SELECT
    -- combine the statutes into an array
    json_group_array(
        json_object(
            'id',
            id,
            'serial_title',
            title,
            'official_title',
            description,
            'statute_date',
            DATE
        )
    ) affected_statutes_list
FROM
    ordered_statutes
