SELECT
  statute_category,
  statute_serial_id
FROM
  {{ statute_references_tbl }}
GROUP BY
  statute_category,
  statute_serial_id
