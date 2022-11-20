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
)
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
    {{ op_cite_tbl }}
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
