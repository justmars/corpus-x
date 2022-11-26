WITH raw_statute_pairs(
    cat,
    idx
) AS (
    -- get the category and serial ids from the opinion statutes table, note that this operates on each item in the bottom-most json group array
    SELECT
        ost.statute_category,
        ost.statute_serial_id
    FROM
        {{ op_stat_tbl }}
        ost
    WHERE
        ost.opinion_id = ot.id
),
ordered_statutes AS (
    -- sort the ids and extract the fields from the statutes table, if they exist
    SELECT
        id,
        title,
        description,
        DATE,
        statute_category,
        statute_serial_id
    FROM
        {{ statute_tbl }}
        s
        JOIN raw_statute_pairs rr
        ON s.statute_category = rr.cat
        AND s.statute_serial_id = rr.idx
    ORDER BY
        DATE DESC
),
excluded_statutes(
    unmatched_pair
) AS (
    -- some raw ids do not yet have statute ids matched because they have not yet been added to the database
    SELECT
        json_group_array(
            json_object(
                'statute_category',
                cat,
                'statute_serial_id',
                idx
            )
        )
    FROM
        raw_statute_pairs x
        LEFT OUTER JOIN ordered_statutes y
        ON x.cat = y.statute_category
        AND x.idx = y.statute_serial_id
    WHERE
        y.id IS NULL
),
included_statutes(statutes) AS (
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
),
raw_citations AS (
    SELECT
        y.docket,
        y.scra,
        y.phil,
        y.offg,
        y.included_decision_id
    FROM
        {{ op_cite_tbl }}
        y
    WHERE
        y.opinion_id = ot.id
),
ordered_decisions AS (
    SELECT
        cited_case.id,
        cited_case.title,
        cited_case.description,
        cited_case.date,
        rc.docket,
        rc.scra,
        rc.phil,
        rc.offg
    FROM
        {{ decision_tbl }}
        cited_case
        JOIN raw_citations rc
        ON cited_case.id = rc.included_decision_id
    ORDER BY
        cited_case.date DESC
),
excluded_decisions(
    unmatched_citations
) AS (
    -- some raw ids do not yet have statute ids matched because they have not yet been added to the database
    SELECT
        json_group_array(
            json_object(
                'docket',
                x.docket,
                'scra',
                x.scra,
                'phil',
                x.phil,
                'offg',
                x.offg
            )
        )
    FROM
        raw_citations x
        LEFT OUTER JOIN ordered_decisions y
        ON (
            (
                x.docket IS NOT NULL
                AND x.docket = y.docket
            )
            OR (
                x.scra IS NOT NULL
                AND x.scra = y.scra
            )
            OR (
                x.phil IS NOT NULL
                AND x.phil = y.phil
            )
            OR (
                x.offg IS NOT NULL
                AND x.offg = y.offg
            )
        )
    WHERE
        y.id IS NULL
),
included_decisions(decisions) AS (
    SELECT
        json_group_array(
            json_object(
                'id',
                id,
                'title',
                title,
                'description',
                description,
                'date',
                DATE
            )
        )
    FROM
        ordered_decisions
)
SELECT
    json_group_array(
        json_object(
            'opinion_id',
            ot.id,
            'title',
            ot.title,
            'justice_id',
            ot.justice_id,
            'text',
            ot.text,
            'statutes',
            (
                SELECT
                    statutes
                FROM
                    included_statutes
            ),
            'unmatched_statutes',
            (
                SELECT
                    unmatched_pair
                FROM
                    excluded_statutes
            ),
            'decisions',
            (
                SELECT
                    decisions
                FROM
                    included_decisions
            ),
            'unmatched_decisions',
            (
                SELECT
                    unmatched_citations
                FROM
                    excluded_decisions
            )
        )
    ) opinions_list
FROM
    {{ opinion_tbl }}
    ot
WHERE
    ot.decision_id = '{{ target_decision_id }}'
