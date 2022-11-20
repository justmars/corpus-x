SELECT
    statute_category cat,
    statute_serial_id idx,
    COUNT(*) num,
    SUM(mentions)
FROM
    {{ op_stat_tbl }}
GROUP BY
    statute_category,
    statute_serial_id
HAVING
    num >= 10
ORDER BY
    num DESC
