SELECT
    docket_category,
    docket_serial,
    COUNT(id) num_entries
FROM
    main.lex_tbl_opinion_citations
WHERE
    included_decision_id IS NULL
    AND docket_category IS NOT NULL
    AND docket_serial IS NOT NULL
GROUP BY
    docket_category,
    docket_serial
HAVING
    num_entries > 3
ORDER BY
    num_entries DESC
