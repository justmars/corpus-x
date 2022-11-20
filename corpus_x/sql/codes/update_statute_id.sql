WITH statutory_base(
    statute_id,
    category,
    serial_id
) AS (
    SELECT
        st.id,
        st.statute_category,
        st.statute_serial_id
    FROM
        {{ statutes_tbl }}
        st
    GROUP BY
        -- probably not the most robust solution but can't use the order by clause within the "update from"; using "group by", the statute_id retrieved is the earliest one.
        st.statute_category,
        st.statute_serial_id
)
UPDATE
    {{ code_tbl }} AS target_tbl -- main table
    SET statute_id = x.statute_id
FROM
    statutory_base x
WHERE
    target_tbl.statute_category = x.category
    AND target_tbl.statute_serial_id = x.serial_id
