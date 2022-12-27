from sqlpyd import Connection

from corpus_x import Statute
from corpus_x.codifications import CodeRow, Codification
from corpus_x.inclusions import (
    CitationInOpinion,
    Inclusion,
    StatuteInOpinion,
    populate_db_with_inclusions,
)


def setup(c: Connection):
    """
    Assumes that (1) tables have been deleted with
    `corpus_x.utils.del_tables.delete_tables_with_prefix()`
    and (2) inclusion `.yaml` files previously been created with
    `corpus_x.inclusions.create_inclusion_files_from_db_opinions()`
    """
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
    for row in c.db[CodeRow.__tablename__].rows:
        CodeRow.set_update_units(c, row["id"])
