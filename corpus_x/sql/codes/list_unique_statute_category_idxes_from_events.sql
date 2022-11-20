SELECT
    statute_category,
    statute_serial_id
FROM
    {{ statute_events_tbl }}
WHERE
    statute_category IS NOT NULL
    AND statute_serial_id IS NOT NULL
GROUP BY
    statute_category,
    statute_serial_id
