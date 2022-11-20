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
            evt.affector_statute_id = base.statute_id
        )
        AND (
            -- the event locator is always present
            evt.locator = base.item
        )
        AND (
            COALESCE(
                -- option 1
                (
                    iif(
                        -- both are present
                        (
                            evt.caption
                            AND evt.content
                        ),
                        -- a match occurs, return early
                        (
                            evt.caption = base.caption
                            AND evt.content LIKE '%' || base.content || '%'
                        ),
                        NULL -- if no match occurs, go to option 2
                    )
                ),
                -- option 2
                (IFNULL(evt.caption, NULL) IS NULL
                OR evt.caption = base.caption),
                -- option 3
                (IFNULL(evt.content, NULL) IS NULL
                OR evt.content LIKE '%' || base.content || '%'),
                1
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
