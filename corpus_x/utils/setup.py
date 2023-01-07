from pathlib import Path

from sqlpyd import Connection


def setup_corpus_x(c: Connection):
    """
    Assumes that (1) tables have been deleted with
    `corpus_x.utils.del_tables.delete_tables_with_prefix()`
    and (2) inclusion `.yaml` files previously been created with
    `corpus_x.inclusions.create_inclusion_files_from_db_opinions()`
    """
    from ..codifications import CodeRow, Codification
    from ..inclusions import (
        CitationInOpinion,
        Inclusion,
        StatuteInOpinion,
        populate_db_with_inclusions,
    )
    from ..resources import corpus_sqlenv
    from ..statutes import Statute

    # initialize tables
    Statute.make_tables(c)
    Inclusion.make_tables(c)
    Codification.make_tables(c)

    # The inclusion tables will be populated from inclusion .yaml files
    populate_db_with_inclusions(c)

    # The inclusion tables will now contain a reference to a statute but the statute doesn't exist yet
    StatuteInOpinion.add_statutes(c)
    StatuteInOpinion.update_statute_ids(c)

    # The inclusion tables will contain a reference to a decision; this needs to be updated with the id
    CitationInOpinion.update_decision_ids(c)

    # Since statutes already exist, can proceed to add codifications
    Codification.add_rows(c)

    # The statutory event data contained in the `units` field does not yet contain the `statute_id`s.
    # Note that, prior to database insertion, we only know the statute label but not the id.
    # Once the statute has been inserted, we can now match the statute label to the id in the deeply
    # nested `units` field of each CodeRow
    for row in c.db[CodeRow.__tablename__].rows:
        CodeRow.set_update_units(c, row["id"])

    # Sample: these are statutes that reference the civil code ordered by the most recent referrer (src)
    # list(c.db["view_src_ref_mp_list"].rows_where("rf_id = ?", ('ra-386-june-18-1949',), select="rf_id, src_statute_id"))
    sql = corpus_sqlenv.get_template("statutes/references/src_ref_mp_list.sql").render()
    c.db.create_view("view_src_ref_mp_list", sql, replace=True)


def setup_x_db(db_path: str) -> Connection:
    """Assuming, pre-setup steps are performed (see pre-inclusions)
    can create and populate tables defined in:

    1. `corpus-pax`
    2. `corpus-base`; and
    3. `corpus-x`

    Args:
        db_path (str): string path to intended database file

    Returns:
        Connection: sqlpyd variant of sqlite-utils / sqlite3 connection wrapper
    """
    from corpus_base import build_sc_tables, init_sc_cases
    from corpus_pax import (
        add_articles_from_api,
        add_individuals_from_api,
        add_organizations_from_api,
        init_person_tables,
    )

    # clear logs
    logs = Path().cwd() / "logs"
    for i in logs.glob("*"):
        if i.is_file():
            i.unlink()
    logs.rmdir()

    # connect
    c = Connection(DatabasePath=db_path, WAL=True)  # type: ignore

    # pax tables
    init_person_tables(c)
    add_individuals_from_api(c)
    add_organizations_from_api(c)
    add_articles_from_api(c)

    # sc tables
    build_sc_tables(c)
    init_sc_cases(c)

    # x tables
    setup_corpus_x(c)
    return c
