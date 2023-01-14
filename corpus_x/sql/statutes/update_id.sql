WITH base AS (
  -- generate the base table to source the update from
  SELECT
    id,
    statute_category,
    statute_serial_id
  FROM
    {{ statute_tbl }}
  GROUP BY
    statute_category,
    statute_serial_id
  ORDER BY
    DATE ASC -- earliest one first in case of variants
)
UPDATE
  {{ target_tbl }} AS xtarget -- add a statute id to the target table (see statutes in opinions, statute references table, etc.)
  set {{ target_col }} = base.id
FROM
  base
WHERE
  xtarget.statute_category = base.statute_category
  AND xtarget.statute_serial_id = base.statute_serial_id
