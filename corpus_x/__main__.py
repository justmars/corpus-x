import json

from corpus_base import DecisionRow, setup_pax_base
from corpus_pax.utils import delete_tables_with_prefix
from sqlpyd import Connection

from .codifications import CodeRow, CodeStatuteEvent, Codification
from .documents import DocRow, Document
from .inclusions import Inclusion, set_inclusions
from .resources import get_authored_object
from .statutes import Statute, StatuteFoundInUnit, StatuteRow


def build_x_tables(c: Connection) -> Connection:
    Statute.make_tables(c)
    Codification.make_tables(c)
    # Document.make_tables(c)
    Inclusion.make_tables(c)
    c.db.index_foreign_keys()
    return c


def setup_x(c: Connection):
    delete_tables_with_prefix(c=c, target_prefixes=["lex_tbl"])
    build_x_tables(c)
    Statute.add_rows(c)
    Codification.add_rows(c)
    set_inclusions(c)


def reset_x(db_path: str):
    """Needs to be connected to the internet because of `setup_pax_base()`"""
    setup_pax_base(db_path)
    c = Connection(DatabasePath=db_path, WAL=True)
    setup_x(c)


def _decode(obj: dict, key: str) -> dict:
    """Convert a string in the `obj` dictionary to a deserialized
    object value."""
    obj[key] = json.loads(obj.pop(key, []))
    return obj


def get_decision(c: Connection, id: str) -> dict:
    obj = get_authored_object(c, DecisionRow.__tablename__, id)
    obj |= Inclusion.get_base_data(c, id)
    obj |= Inclusion.list_opinions_of_decision(c, id)
    obj = _decode(obj, "author_list")
    obj = _decode(obj, "opinions_list")
    for opinion in obj["opinions_list"]:
        opinion = _decode(opinion, "statutes")
        opinion = _decode(opinion, "unmatched_statutes")
        opinion = _decode(opinion, "decisions")
        opinion = _decode(opinion, "unmatched_decisions")
    return obj


def get_codification(c: Connection, id: str) -> dict:
    obj = get_authored_object(c, CodeRow.__tablename__, id)
    obj |= CodeRow.get_base_data(c, id)
    obj |= CodeStatuteEvent.list_event_statutes(c, id)
    obj = _decode(obj, "statute_titles")
    obj = _decode(obj, "units")
    obj = _decode(obj, "author_list")
    obj = _decode(obj, "event_statute_affectors")
    return obj


def get_statute(c: Connection, id: str) -> dict:
    obj = get_authored_object(c, StatuteRow.__tablename__, id)
    obj |= StatuteRow.get_base_data(c, id)
    obj |= StatuteFoundInUnit.list_affected_statutes(c, id)
    obj |= StatuteFoundInUnit.list_affector_statutes(c, id)
    obj = _decode(obj, "statute_titles")
    obj = _decode(obj, "code_titles")
    obj = _decode(obj, "units")
    obj = _decode(obj, "author_list")
    obj = _decode(obj, "affected_statutes_list")
    obj = _decode(obj, "affector_statutes_list")
    return obj


def get_document(c: Connection, id: str) -> dict:
    obj = get_authored_object(c, DocRow.__tablename__, id)
    # obj = _decode(obj, "units"), needs to be implemented via .get_base_data()
    obj = _decode(obj, "author_list")
    return obj
