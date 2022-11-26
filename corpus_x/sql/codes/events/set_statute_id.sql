-- the statute in the event table, is the title of the statutes table.
WITH evt AS (
    SELECT
        id,
        material_path,
        statute,
        variant,
        DATE
    FROM
        {{ event_tbl }}
),
-- use the statutes table (basis) to update the codification events table (target)
base AS (
    SELECT
        id,
        title,
        -- the title is serial title (see statute-trees 0.0.17)
        variant,
        DATE
    FROM
        {{ statute_tbl }}
),
events_matched AS (
    SELECT
        evt.id event_id,
        evt.material_path mp,
        evt.statute serial_statute,
        evt.variant event_variant,
        evt.date event_date,
        base.id statute_id,
        base.variant statute_variant,
        base.date statute_date
    FROM
        evt
        JOIN base
    WHERE
        evt.statute = base.title -- the title is serial title (see statute-trees 0.0.17)
        AND (
            (IFNULL(evt.date, NULL) IS NULL
            OR evt.date = base.date)
            AND (IFNULL(evt.variant, NULL) IS NULL
            OR evt.variant = base.variant)
        )
    GROUP BY
        event_id
)
UPDATE
    {{ event_tbl }} AS ce -- will modify each affector_id
    set affector_statute_id = events_matched.statute_id
FROM
    events_matched
WHERE
    ce.id = events_matched.event_id
