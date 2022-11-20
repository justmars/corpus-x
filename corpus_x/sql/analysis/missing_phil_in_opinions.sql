SELECT
    phil,
    included_decision_id,
    COUNT(id) num_entries
FROM
    main.lex_tbl_opinion_citations
WHERE
    phil IS NOT NULL
    AND included_decision_id IS NULL
GROUP BY
    phil
HAVING
    num_entries > 3
ORDER BY
    num_entries DESC
