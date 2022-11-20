SELECT
    dt.source,
    dt.origin,
    op.decision_id,
    op.text,
    op.id opinion_id
FROM
    {{ opinion_tbl }}
    op
    JOIN {{ decision_tbl }}
    dt
WHERE
    dt.id = op.decision_id
