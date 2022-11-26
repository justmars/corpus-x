SELECT
    codification_id,
    locator,
    caption,
    content,
    statute,
    variant,
    DATE
FROM
    {{ event_tbl }}
WHERE
    affector_material_path IS NULL
