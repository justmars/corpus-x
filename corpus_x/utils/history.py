from sqlite_utils.db import Table
from sqlpyd import Connection


def detect_statute_mp(code_pk: str, stat_id: str, tbl: Table, h: dict):
    mps, loc, cap, cont = (
        None,
        h.get("locator"),
        h.get("caption"),
        h.get("content"),
    )
    if all([loc, cap, cont, stat_id]):
        mps = list(
            tbl.rows_where(
                """codification_id = ? and locator = ?
                and caption = ? and content = ? and affector_statute_id = ?""",
                (code_pk, loc, cap, cont, stat_id),
                select="affector_material_path",
            )
        )
    elif all([loc, cap, stat_id]):
        mps = list(
            tbl.rows_where(
                """codification_id = ? and locator = ? and caption = ?
                and affector_statute_id = ?""",
                (code_pk, loc, cap, stat_id),
                select="affector_material_path",
            )
        )
    elif all([loc, cont, stat_id]):
        mps = list(
            tbl.rows_where(
                """codification_id = ? and locator = ? and content = ?
                and affector_statute_id = ?""",
                (code_pk, loc, cont, stat_id),
                select="affector_material_path",
            )
        )
    elif all([loc, stat_id]):
        mps = list(
            tbl.rows_where(
                """codification_id = ? and locator = ?
                and affector_statute_id = ?""",
                (code_pk, loc, stat_id),
                select="affector_material_path",
            )
        )
    if mps:
        if stat_mp := mps[0]["affector_material_path"]:
            return stat_mp
    return None


def detect_statute_id(code_pk: str, tbl: Table, h: dict):
    rows, stat, dt, vt = (
        None,
        h.get("statute"),
        h.get("date"),
        h.get("variant"),
    )
    if all([stat, dt, vt]):
        q = "codification_id = ? and statute = ? and date = ? and variant = ?"
        rows = list(
            tbl.rows_where(
                q,
                (code_pk, stat, dt, vt),
                select="affector_statute_id",
            )
        )
    elif all([stat, dt]):
        q = "codification_id = ? and statute = ? and date = ?"
        rows = list(
            tbl.rows_where(
                q,
                (code_pk, stat, dt),
                select="affector_statute_id",
            )
        )
    elif all([stat, vt]):
        q = "codification_id = ? and statute = ? and variant = ?"
        rows = list(
            tbl.rows_where(
                q,
                (code_pk, stat, vt),
                select="affector_statute_id",
            )
        )
    else:
        q = "codification_id = ? and statute = ?"
        rows = list(
            tbl.rows_where(
                q,
                (code_pk, stat),
                select="affector_statute_id",
            )
        )
    if rows:
        if stat_id := rows[0]["affector_statute_id"]:
            return stat_id
    return None


def detect_case_id(code_pk: str, tbl: Table, h: dict):
    if cite := h.get("citation"):
        if rows := list(
            tbl.rows_where(
                "codification_id = ? and citation = ?",
                (code_pk, cite),
                select="affector_decision_id",
            )
        ):
            return rows[0]["affector_decision_id"]


def set_histories(code_pk: str, nodes: list[dict], c: Connection):
    from corpus_base.decision import DecisionRow

    from corpus_x.codifications import CodeCitationEvent, CodeStatuteEvent
    from corpus_x.statutes import StatuteRow

    ct_evt = c.db[CodeCitationEvent.__tablename__]
    st_evt = c.db[CodeStatuteEvent.__tablename__]
    st = c.db[StatuteRow.__tablename__]
    dec = c.db[DecisionRow.__tablename__]
    for node in nodes:
        if h_list := node.get("history", None):
            for h in h_list:
                case_id = detect_case_id(code_pk, ct_evt, h)  # type: ignore
                if case_id:
                    case_date = dec.get(case_id)["date"]  # type: ignore
                    h["decision_id"] = case_id
                    h["decision_date"] = case_date

                stat_id = detect_statute_id(code_pk, st_evt, h)  # type: ignore
                if stat_id:
                    stat_date = st.get(stat_id)["date"]  # type: ignore
                    h["statute_id"] = stat_id
                    h["statute_date"] = stat_date
                    elements = (code_pk, stat_id, st_evt, h)
                    mp = detect_statute_mp(*elements)  # type: ignore
                    if mp:
                        h["statute_mp"] = mp
        if subunits := node.get("units"):
            set_histories(code_pk, subunits, c)
