SELECT
    scra,
    included_decision_id,
    COUNT(id) num_entries
FROM
    main.lex_tbl_opinion_citations
WHERE
    scra IS NOT NULL
    AND included_decision_id IS NULL
GROUP BY
    scra
HAVING
    num_entries > 3
ORDER BY
    num_entries DESC
