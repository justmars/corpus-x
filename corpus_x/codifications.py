import json
import sqlite3
from collections.abc import Iterator
from pathlib import Path

from corpus_base.decision import CitationRow, DecisionRow
from pydantic import EmailStr, Field
from sqlpyd import Connection, TableConfig
from statute_patterns import Rule, StatuteSerialCategory
from statute_patterns.components.utils import DETAILS_FILE
from statute_trees import (
    CitationAffector,
    CodePage,
    CodeUnit,
    Page,
    StatuteAffector,
    StatuteBase,
    generic_content,
    generic_mp,
)

from .resources import CODIFICATION_FILES, Integrator, corpus_sqlenv
from .statutes import Statute, StatuteMaterialPath, StatuteRow, StatuteTitleRow
from .utils import logger, set_histories


class CodeRow(Page, StatuteBase, TableConfig):
    __prefix__ = "lex"
    __tablename__ = "codifications"
    __indexes__ = [["statute_category", "statute_serial_id"]]

    @classmethod
    def get_id(cls, c: Connection, pk: str) -> str | None:
        tbl = c.table(cls)
        q = "id = ?"
        rows = list(tbl.rows_where(where=q, where_args=(pk,), select="id"))
        idx = rows[0]["id"] if rows else None
        return idx

    @classmethod
    def get_base_data(cls, c: Connection, pk: str) -> dict:
        sql_file = "codes/get_base.sql"
        template = corpus_sqlenv.get_template(sql_file)
        results = c.db.execute_returning_dicts(
            template.render(
                target_code_id=pk,
                code_tbl=cls.__tablename__,
                statute_tbl=StatuteRow.__tablename__,
                statute_title_tbl=StatuteTitleRow.__tablename__,
            )
        )
        if results:
            return results[0]
        return {}

    @classmethod
    def set_update_units(cls, c: Connection, pk: str) -> str:
        """Using data from codification events, add the `material_path`
        and `statute_id` of the affecting statute to each history node
        of the original `units` field."""
        tbl = c.db[cls.__tablename__]
        nodes = json.loads(tbl.get(pk)["units"])  # type: ignore
        set_histories(pk, nodes, c)  # recursive; updates nodes _in place_
        tbl.update(pk, {"units": json.dumps(nodes)})  # type: ignore
        return pk


class CodeUnitSearch(TableConfig):
    __prefix__ = "lex"
    __tablename__ = "codification_fts_units"
    __indexes__ = [["codification_id", "material_path"]]
    codification_id: str = Field(
        ..., col=str, fk=(CodeRow.__tablename__, "id")
    )
    material_path: str = generic_mp
    unit_text: str = generic_content


class CodeCitationEvent(CitationAffector, TableConfig):
    __prefix__ = "lex"
    __tablename__ = "codification_events_citation"
    __indexes__ = [["codification_id", "material_path"]]
    codification_id: str = Field(
        ..., col=str, fk=(CodeRow.__tablename__, "id")
    )
    material_path: str = generic_mp
    affector_decision_id: str = Field(
        None,
        description=(
            "The historical event is"
            " affected by a decision found in the decisions table."
        ),
        col=str,
        fk=(DecisionRow.__tablename__, "id"),
    )

    @classmethod
    def extract_units(cls, pk: str, units: list["CodeUnit"]):
        """Given a list of code units, extract affected units
        with their associated historical events."""
        for u in units:
            if u.history:
                for evt in u.history:
                    if isinstance(evt, CitationAffector):
                        yield CodeCitationEvent(
                            **evt.dict(),
                            material_path=u.id,
                            codification_id=pk,
                        )
            if u.units:
                yield from cls.extract_units(pk, u.units)

    @classmethod
    def update_decision_ids(cls, c: Connection):
        sql_file = "codes/events/set_decision_id.sql"
        template = corpus_sqlenv.get_template(sql_file)
        with c.session as cur:
            return cur.execute(
                template.render(
                    citation_tbl=CitationRow.__tablename__,
                    event_tbl=cls.__tablename__,
                )
            )


class CodeStatuteEvent(StatuteAffector, TableConfig):
    """Each `StatuteAffector` is a history node which takes into account
    a possible `date` and `variant` field to deal with duplicates.
    If they are present, these are used to detect the `affector_statute_id`.
    """

    __prefix__ = "lex"
    __tablename__ = "codification_events_statute"
    __indexes__ = [
        [
            "locator",
            "caption",
            "content",
            "statute_category",
            "statute_serial_id",
            "variant",
            "date",
        ],
        [
            "locator",
            "caption",
            "content",
            "statute_category",
            "statute_serial_id",
            "date",
        ],
        [
            "locator",
            "caption",
            "content",
            "statute_category",
            "statute_serial_id",
            "variant",
        ],
        [
            "locator",
            "caption",
            "content",
            "statute_category",
            "statute_serial_id",
        ],
        ["locator", "caption", "statute"],
        ["locator", "content", "statute"],
        ["locator", "statute"],
        ["codification_id", "material_path"],
        ["affector_statute_id", "affector_material_path"],
    ]
    codification_id: str = Field(
        ..., col=str, fk=(CodeRow.__tablename__, "id")
    )
    material_path: str = generic_mp
    affector_material_path: str | None = Field(None, col=str, index=True)
    affector_statute_unit_id: int = Field(
        None, col=str, fk=(StatuteMaterialPath.__tablename__, "id")
    )
    affector_statute_id: str | None = Field(
        None, col=str, fk=(StatuteRow.__tablename__, "id")
    )

    @classmethod
    def list_event_statutes(cls, c: Connection, pk: str) -> dict:
        sql_file = "codes/list_event_statutes.sql"
        template = corpus_sqlenv.get_template(sql_file)
        results = c.db.execute_returning_dicts(
            template.render(
                event_tbl=cls.__tablename__,
                statute_tbl=StatuteRow.__tablename__,
                target_id=pk,
            )
        )
        if results:
            return results[0]
        return {}

    @classmethod
    def extract_units(cls, pk: str, units: list["CodeUnit"]):
        """Given a list of code units, extract affected units
        with their associated historical events.
        """
        for u in units:
            if u.history:
                for evt in u.history:
                    if isinstance(evt, StatuteAffector):
                        yield cls(
                            **evt.dict(exclude_none=True),
                            material_path=u.id,
                            codification_id=pk,
                        )
            if u.units:
                yield from cls.extract_units(pk, u.units)

    @classmethod
    def get_statutes_from_events(cls, c: Connection) -> Iterator[dict]:
        """Extract relevant statute category and identifier pairs
        from the Codification Events table.
        """
        sql_file = "codes/list_unique_statute_category_idxes_from_events.sql"
        template = corpus_sqlenv.get_template(sql_file)
        q = template.render(statute_events_tbl=cls.__tablename__)
        for row in c.db.execute_returning_dicts(q):
            cat = row["statute_category"]
            idx = row["statute_serial_id"]
            if cat and idx:
                yield {"cat": cat, "id": idx}
            else:
                logger.error(f"Missing cat and idx in {row=}")
                continue

    @classmethod
    def add_statutes_from_events(cls, c: Connection):
        """Get `StatuteBases`; For each `StatuteBase`, extract possible
        folders. For each specific statute folder, setup a `Statute` object
        by extracting data from the folder and inserting the same into
        the database `db`."""
        for x in cls.get_statutes_from_events(c):
            rule = Rule(cat=StatuteSerialCategory(x["cat"]), id=x["id"])
            folders = rule.extract_folders()
            for folder in folders:
                content = folder / DETAILS_FILE
                detail = Rule.get_details(content)
                if not detail:
                    logger.error(f"Could not extract detail; {folder=}")
                    continue

                if is_existing_idx := StatuteRow.get_id(c, detail.id):
                    logger.debug(f"Existing statute: {is_existing_idx}")
                    continue

                else:
                    logger.debug(f"Attempt {rule=}; pk {folder.stem=}")
                    obj = Statute.from_page(content)
                    obj.insert_objects(c, StatuteRow, obj.relations)
                    logger.debug(f"Created statute: {obj}")

    @classmethod
    def update_statute_ids(cls, c: Connection) -> sqlite3.Cursor:
        """After running `cls.add_statutes_from_events()`, all Statutes
        contained in Codification statutory events will be present in
        the `db`. Supply the `affector_statute_id` of the
        CodeStatuteEvent table."""
        sql_file = "codes/events/set_statute_id.sql"
        template = corpus_sqlenv.get_template(sql_file)
        with c.session as cur:
            return cur.execute(
                template.render(
                    event_tbl=cls.__tablename__,
                    statute_tbl=StatuteRow.__tablename__,
                )
            )

    @classmethod
    def update_unit_ids(cls, c: Connection) -> sqlite3.Cursor:
        """After running `cls.update_affector_statute_ids()`, all statute
        affector ids have been updated. Supply the `affector_statute_unit_id`
        and  `affector_statute_unit_material_path` of the CodeStatuteEvent
        table."""
        sql_file = "codes/events/set_statute_unit_mp.sql"
        template = corpus_sqlenv.get_template(sql_file)
        with c.session as cur:
            return cur.execute(
                template.render(
                    event_tbl=cls.__tablename__,
                    mp_tbl=StatuteMaterialPath.__tablename__,
                )
            )

    @classmethod
    def fetch_unmaterialized(cls, c: Connection) -> list[dict] | None:
        """Search for unit events which were unable to get an
        affector material path."""
        sql_file = "codes/events/search_unmaterialized.sql"
        if rows := c.db.execute_returning_dicts(
            corpus_sqlenv.get_template(sql_file).render(
                event_tbl=cls.__tablename__,
            )
        ):
            return rows
        return None


class Codification(Integrator):
    id: str
    meta: CodeRow
    emails: list[EmailStr]
    tree: list[CodeUnit]
    unit_fts: list[CodeUnitSearch]
    stat_events: list[CodeStatuteEvent]
    cite_events: list[CodeCitationEvent]

    @property
    def relations(self):
        return [
            (CodeUnitSearch, self.unit_fts),
            (CodeStatuteEvent, self.stat_events),
            (CodeCitationEvent, self.cite_events),
        ]

    @classmethod
    def make_tables(cls, c: Connection):
        c.create_table(CodeRow)
        c.create_table(CodeUnitSearch)
        if c.table(StatuteRow):
            c.create_table(CodeStatuteEvent)
        if c.table(DecisionRow):
            c.create_table(CodeCitationEvent)

    @classmethod
    def add_rows(cls, c: Connection):
        # setup each codification row
        for raw_code in CODIFICATION_FILES:
            obj = cls.from_page(raw_code)
            idx = obj.insert_objects(c, CodeRow, obj.relations)
            logger.debug(f"Added codification {idx=} from {raw_code.stem=}")

        # add the base statute of codification by first transforming the table
        c.db[CodeRow.__tablename__].add_column(  # type: ignore
            col_name="statute_id",
            col_type=str,
            fk=StatuteRow.__tablename__,
            fk_col="id",
        )
        c.db.execute(
            corpus_sqlenv.get_template("codes/update_statute_id.sql").render(
                code_tbl=CodeRow.__tablename__,
                statutes_tbl=StatuteRow.__tablename__,
            )
        )

        # set events then update original trees
        CodeStatuteEvent.add_statutes_from_events(c)  # populate statutes table
        CodeStatuteEvent.update_statute_ids(c)  # needed to update tree
        CodeStatuteEvent.update_unit_ids(c)  # needed to update tree
        CodeCitationEvent.update_decision_ids(c)
        # update original trees
        [
            CodeRow.set_update_units(c, row["id"])
            for row in c.db[CodeRow.__tablename__].rows
        ]

    @classmethod
    def from_page(cls, file_path: Path):
        # build and validate metadata from the path
        page = CodePage.build(file_path)
        if not page:
            raise Exception(f"No page from {file_path=}")

        # assign row for creation
        meta = page.dict(exclude={"tree", "emails"})

        # enable full text searches of contents of the tree; starts with `1.1.`
        fts = [
            CodeUnitSearch(**unit)
            for unit in CodeUnit.searchables(pk=page.id, units=page.tree)
        ]

        # full text searches should includes a title row, i.e. node `1.``
        root_fts = [
            CodeUnitSearch(
                codification_id=page.id,
                material_path="1.",
                unit_text=", ".join(
                    [
                        f"{page.statute_category} {page.statute_serial_id}",
                        f"{page.title}",
                        f"{page.description}",
                    ]
                ),
            )
        ]

        return cls(
            id=page.id,
            emails=page.emails,
            meta=CodeRow(**meta),
            tree=page.tree,
            unit_fts=root_fts + fts,
            stat_events=list(
                CodeStatuteEvent.extract_units(pk=page.id, units=page.tree)
            ),
            cite_events=list(
                CodeCitationEvent.extract_units(pk=page.id, units=page.tree)
            ),
        )
