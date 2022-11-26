WITH raw_statute_pairs(
    cat,
    idx,
    dt
) AS (
    -- get the category and serial id that is affected (from the statutes table)
    SELECT
        statute_category,
        statute_serial_id,
        DATE
    FROM
        {{ statute_tbl }}
    WHERE
        id = '{{ affected_statute_id }}'
),
affectors(id) AS (
    -- based on the category and serial ids from the statute references table, determine which statute ids affect the target_refs
    SELECT
        ref.statute_id
    FROM
        {{ ref_tbl }}
        ref
        JOIN raw_statute_pairs rr
        ON ref.statute_category = rr.cat
        AND ref.statute_serial_id = rr.idx
),
ordered_statutes AS (
    -- sort the ids and extract the fields from the statutes table; note that the ids must be newer than the original statute described by target_refs
    SELECT
        id,
        title,
        description,
        DATE
    FROM
        {{ statute_tbl }}
    WHERE
        id IN affectors
        AND DATE > (
            SELECT
                dt
            FROM
                raw_statute_pairs
        )
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
    ) affector_statutes_list
FROM
    ordered_statutes
