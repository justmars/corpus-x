SELECT
    justice_id,
    per_curiam,
    composition,
    category
FROM
    {{ decision_tbl }}
WHERE
    id = '{{ target_decision_id }}'
