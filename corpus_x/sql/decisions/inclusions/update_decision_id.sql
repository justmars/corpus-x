WITH decision_data(id) AS (
    SELECT
        dct.decision_id
    FROM
        {{ cite_tbl }}
        dct
    WHERE
        dct.docket = oct.docket
        OR dct.scra = oct.scra
        OR dct.phil = oct.phil
        OR dct.offg = oct.offg
),
matched_data AS (
    SELECT
        oct.docket,
        oct.scra,
        oct.phil,
        oct.offg,
        COUNT(*) num,
        (
            SELECT
                id
            FROM
                decision_data
        ) decision_id
    FROM
        {{ target_tbl }}
        oct
    GROUP BY
        oct.docket,
        oct.scra,
        oct.phil,
        oct.offg
    HAVING
        num > 3
    ORDER BY
        num DESC
)
UPDATE
    {{ target_tbl }} AS loc -- match the decision id found based on the docket
    SET {{ target_col }} = matched_data.decision_id
FROM
    matched_data
WHERE
    loc.docket = matched_data.docket
    OR loc.scra = matched_data.scra
    OR loc.phil = matched_data.phil
    OR loc.offg = matched_data.offg
