WITH statutory_ids(ids) AS (
    -- get the ids from the code events table
    SELECT
        DISTINCT(affector_statute_id)
    FROM
        {{ event_tbl }}
    WHERE
        codification_id = '{{ target_id }}'
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
    WHERE
        id IN statutory_ids
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
    ) event_statute_affectors
FROM
    ordered_statutes
