from sqlpyd import Connection


def delete_tables_with_prefix(c: Connection, target_prefixes: list[str]):
    """Delete tables containing  `table_prefix-` found in  database
    connection `c`."""
    for p in target_prefixes:
        sql = f"""--sql
            select name
            from sqlite_schema
            where type='table' and name like '{p}%'
            order by name;
            """
        for row in c.db.execute_returning_dicts(sql):
            c.db.execute(
                f"""--sql
                drop table if exists {row['name']};
            """
            )
