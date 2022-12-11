WITH evt AS (
    SELECT
        id,
        material_path,
        locator,
        caption,
        content,
        codification_id,
        affector_statute_id
    FROM
        {{ event_tbl }}
),
-- get list of statutory events
base AS (
    SELECT
        id,
        material_path,
        item,
        caption,
        content,
        statute_id
    FROM
        {{ mp_tbl }}
),
-- get candidate units from the statutes table
events_matched AS (
    SELECT
        evt.locator,
        evt.caption,
        evt.content,
        evt.id AS target_event_id,
        evt.codification_id,
        base.id affector_unit_id,
        base.material_path affector_material_path,
        base.statute_id
    FROM
        evt
        JOIN base
        ON (
            -- the affector statute id needs to have previously set (see update_statute_id_in_events.sql)
            base.statute_id = evt.affector_statute_id
        )
        AND (
            -- the event locator is always present
            base.item = evt.locator
        )
        AND (
            (
                -- will evaluate to true if empty; will return the comparison result as a boolean if true / false
                evt.caption IS NULL
                OR base.caption = evt.caption
            )
            AND (
                -- the same treatment (null or true, see sqlite) is applied to content but now qualified by the like operator
                evt.content IS NULL
                OR base.content LIKE '%' || evt.content || '%'
            )
        )
)
UPDATE
    {{ event_tbl }} AS ce -- table to update
    --  the fields are the unit affector's and id and material path
    set affector_material_path = events_matched.affector_material_path,
    affector_statute_unit_id = events_matched.affector_unit_id
FROM
    events_matched
WHERE
    events_matched.target_event_id = ce.id
