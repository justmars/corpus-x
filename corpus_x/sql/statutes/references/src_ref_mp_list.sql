/*
Question 1: How many references are made by a source (src) statute to a referenced (rf) statute?

Question 2: What is list of material paths from src statute that affect the reference statute

*/
SELECT
    (
        SELECT
            DATE
        FROM
            lex_tbl_statutes
        WHERE
            id = ref.statute_id
    ) src_date,
    -- date of the origin
    ref.statute_id src_statute_id,
    -- where the references originate
    referenced.id rf_id,
    -- referenced statute id
    referenced.date rf_date,
    -- date of the referenced statute
    COUNT(
        ref.material_path
    ) mp_count_of_rf_in_src,
    json_group_array(
        ref.material_path
    ) src_mp_list -- where in the origin the references come from; this is a lst of material paths since there may be many references
FROM
    lex_tbl_statute_unit_references ref
    JOIN lex_tbl_statutes referenced
    ON referenced.statute_category = ref.statute_category
    AND referenced.statute_serial_id = ref.statute_serial_id
WHERE
    rf_date < src_date -- the referenced statute must be earlier than the origin since the reference must exist first
GROUP BY
    rf_id,
    -- each origin will contain multiple references, grouping by the referenced statute per src = number of times the source mentionds the reference statute
    src_statute_id
ORDER BY
    src_date DESC
