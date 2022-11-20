WITH citation_base AS (
    -- look for a decision id matching the citation
    SELECT
        decision_id
    FROM
        {{ citation_tbl }}
    WHERE
        (
            docket IS NOT NULL
            AND docket = citation
        )
        OR (
            scra IS NOT NULL
            AND scra = citation
        )
        OR (
            phil IS NOT NULL
            AND phil = citation
        )
        OR (
            offg IS NOT NULL
            AND phil = citation
        )
),
events_matched(
    code_cite_evt_id,
    citation,
    decision_id
) AS (
    -- map the matching decision_id to the code event id
    SELECT
        id,
        LOWER(DISTINCT(citation)),
        (
            SELECT
                decision_id
            FROM
                citation_base
        )
    FROM
        {{ event_tbl }}
)
UPDATE
    {{ event_tbl }} AS ce -- update the code event row with the matched decision id
    set affector_decision_id = events_matched.decision_id
FROM
    events_matched
WHERE
    ce.id = events_matched.code_cite_evt_id
    AND events_matched.decision_id IS NOT NULL
