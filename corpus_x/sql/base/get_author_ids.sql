SELECT
    json_group_array(
        json_object(
            'id',
            i.id,
            'display',
            i.display_name,
            'img',
            i.img_id
        )
    ) author_list
FROM
    pax_tbl_individuals i
WHERE
    i.id IN (
        SELECT
            {{ col_author_id }}
        FROM
            {{ generic_tbl }}
        WHERE
            {{ col_generic_obj }} = '{{ target_id }}'
    )
