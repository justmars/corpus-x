from pathlib import Path

from corpus_pax.utils import delete_tables_with_prefix
from sqlpyd import Connection

from ._loggers import clear_logs


def setup_corpus_x(c: Connection):
    """
    Setup requires a prior step not included here.

    It assumes that:

    1. corpus-x tables do not yet exist; or have been deleted with
    `corpus_x.utils.del_tables.delete_tables_with_prefix()`

    2. inclusion `.yaml` files were previously been created with
    `corpus_x.inclusions.create_inclusion_files_from_db_opinions()`

    The inclusion files ensure that `populate_db_with_inclusions()`
    will run properly.
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

    # reset tables
    delete_tables_with_prefix(c=c, target_prefixes=["lex"])

    # initialize tables
    Statute.make_tables(c)
    Inclusion.make_tables(c)
    Codification.make_tables(c)

    # The inclusion tables will be populated from inclusion .yaml files
    populate_db_with_inclusions(c)

    # The inclusion tables will now contain a reference to a statute
    # but the statute doesn't exist yet
    StatuteInOpinion.add_statutes(c)
    StatuteInOpinion.update_statute_ids(c)

    # The inclusion tables will contain a reference to a decision;
    # this needs to be updated with the id
    CitationInOpinion.update_decision_ids(c)

    # Since statutes already exist, can proceed to add codifications
    Codification.add_rows(c)

    # The statutory event data contained in the `units` field does
    # not yet contain the `statute_id`s.
    #
    # Note that, prior to database insertion, we only know the statute label
    # but not the id.
    #
    # Once the statute has been inserted, we can now match the statute label
    # to the id in the deeply nested `units` field of each CodeRow
    for row in c.db[CodeRow.__tablename__].rows:
        CodeRow.set_update_units(c, row["id"])

    # Sample: these are statutes that reference the civil code ordered
    # by the most recent referrer (src)
    # list(c.db["view_src_ref_mp_list"].rows_where(
    #   "rf_id = ?",
    #   ('ra-386-june-18-1949',),
    #   select="rf_id, src_statute_id"
    # ))
    sql = corpus_sqlenv.get_template(
        "statutes/references/src_ref_mp_list.sql"
    ).render()
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
    from corpus_base import setup_base
    from corpus_pax import setup_pax

    # clear logs
    clear_logs()
    setup_pax(db_path)
    setup_base(db_path)

    # connect
    c = Connection(DatabasePath=db_path, WAL=True)  # type: ignore

    setup_corpus_x(c)
    return c
