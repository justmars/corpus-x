import sqlite3
from collections.abc import Iterator
from pathlib import Path
from sqlite3 import IntegrityError

from pydantic import EmailStr, Field, ValidationError
from sqlpyd import Connection, TableConfig
from statute_patterns import (
    Rule,
    StatuteSerialCategory,
    StatuteTitleCategory,
    extract_rules,
)
from statute_trees import (
    Node,
    Page,
    StatuteBase,
    StatutePage,
    StatuteUnit,
    generic_content,
    generic_mp,
)

from .resources import STATUTE_FILES, STATUTE_PATH, Integrator, corpus_sqlenv
from .utils import logger


class StatuteRow(Page, StatuteBase, TableConfig):
    """This corresponds to statute_trees.StatutePage but is adjusted
    for the purpose of table creation."""

    __prefix__ = "lex"
    __tablename__ = "statutes"
    __indexes__ = [
        ["statute_category", "statute_serial_id", "date", "variant"],
        ["statute_category", "statute_serial_id", "date"],
        ["statute_category", "statute_serial_id", "variant"],
        ["statute_category", "statute_serial_id"],
    ]

    @classmethod
    def get_base_data(cls, c: Connection, pk: str) -> dict:
        from .codifications import CodeRow

        sql_file = "statutes/get_base.sql"
        template = corpus_sqlenv.get_template(sql_file)
        results = c.db.execute_returning_dicts(
            template.render(
                target_statute_id=pk,
                statute_tbl=cls.__tablename__,
                statute_title_tbl=StatuteTitleRow.__tablename__,
                statute_references_tbl=StatuteFoundInUnit.__tablename__,
                code_tbl=CodeRow.__tablename__,
            )
        )
        if results:
            return results[0]
        return {}

    @classmethod
    def get_id_via_catid(cls, c: Connection, cat: str, id: str) -> str | None:
        tbl = c.table(cls)
        q = "statute_category = ? and statute_serial_id = ?"
        rows = list(tbl.rows_where(where=q, where_args=(cat, id), select="id"))
        idx = rows[0]["id"] if rows else None
        return idx

    @classmethod
    def get_id(cls, c: Connection, pk: str) -> str | None:
        tbl = c.table(cls)
        q = "id = ?"
        rows = list(tbl.rows_where(where=q, where_args=(pk,), select="id"))
        idx = rows[0]["id"] if rows else None
        return idx


class StatuteTitleRow(TableConfig):
    """This corresponds to statute_patterns.StatuteTitle but
    is adjusted for the purpose of table creation."""

    __prefix__ = "lex"
    __tablename__ = "statute_titles"
    __indexes__ = [["category", "text"], ["category", "statute_id"]]
    statute_id: str = Field(..., col=str, fk=(StatuteRow.__tablename__, "id"))
    category: StatuteTitleCategory = Field(
        ...,
        col=str,
        index=True,
    )
    text: str = Field(..., col=str, fts=True)

    class Config:
        use_enum_values = True


class StatuteUnitSearch(TableConfig):
    __prefix__ = "lex"
    __tablename__ = "statute_fts_units"
    __indexes__ = [["statute_id", "material_path"]]
    statute_id: str = Field(..., col=str, fk=(StatuteRow.__tablename__, "id"))
    material_path: str = generic_mp
    unit_text: str = generic_content


class StatuteMaterialPath(Node, TableConfig):
    __prefix__ = "lex"
    __tablename__ = "statute_mp_units"
    __indexes__ = [
        ["item", "caption", "content", "statute_id"],
        ["item", "caption", "statute_id"],
        ["item", "content", "statute_id"],
        ["item", "statute_id"],
    ]
    statute_id: str = Field(..., col=str, fk=(StatuteRow.__tablename__, "id"))
    material_path: str = generic_mp


class StatuteFoundInUnit(StatuteBase, TableConfig):
    """Each unit in Statute A (see MP) may refer to Statute B.
    Statute B is referenced through it's category and identifier
    (hence inheriting from `StatuteBase`). After securing the category
    and identifier pairs, can use the `cls.update_statute_ids()` to
    supply the matching statute  id of the category/identifier pair.
    """

    __prefix__ = "lex"
    __tablename__ = "statute_unit_references"
    __indexes__ = [
        ["statute_category", "statute_serial_id"],
        ["statute_category", "statute_id"],
    ]
    statute_id: str = Field(..., col=str, fk=(StatuteRow.__tablename__, "id"))
    material_path: str = generic_mp
    matching_statute_id: str | None = Field(
        None,
        description=(
            "Each unit in Statute A (see MP) may refer to Statute B."
            " Statute B is referenced through it's category and identifier"
            " (see StatuteBase)."
        ),
        col=str,
        fk=(StatuteRow.__tablename__, "id"),
    )

    @classmethod
    def list_affected_statutes(cls, c: Connection, pk: str) -> dict:
        sql_file = "statutes/list_affected_statutes.sql"
        results = c.db.execute_returning_dicts(
            corpus_sqlenv.get_template(sql_file).render(
                ref_tbl=cls.__tablename__,
                statute_tbl=StatuteRow.__tablename__,
                affecting_statute_id=pk,
            )
        )
        if results:
            return results[0]
        return {}

    @classmethod
    def list_affector_statutes(cls, c: Connection, pk: str) -> dict:
        sql_file = "statutes/list_affector_statutes.sql"
        results = c.db.execute_returning_dicts(
            corpus_sqlenv.get_template(sql_file).render(
                ref_tbl=cls.__tablename__,
                statute_tbl=StatuteRow.__tablename__,
                affected_statute_id=pk,
            )
        )
        if results:
            return results[0]
        return {}

    @classmethod
    def find_statute_in_unit(
        cls,
        text: str,
        mp: str,
        statute_id: str,
    ) -> Iterator["StatuteFoundInUnit"]:
        """Given text of a particular `material_path`, determine if there are
        statutes found by `get_statute_labels`; if they're found, determine
        the proper `StatuteFoundInUnit` to yield.
        """
        for rule in extract_rules(text):
            yield cls(
                material_path=mp,
                statute_id=statute_id,
                statute_category=rule.cat,
                statute_serial_id=rule.id,
                matching_statute_id=None,
            )

    @classmethod
    def extract_units(
        cls,
        pk: str,
        units: list["StatuteUnit"],
    ) -> Iterator["StatuteFoundInUnit"]:
        """Traverse the tree and search the caption and content of each unit
        for possible Statutes.
        """
        for u in units:
            if u.caption and u.content:
                text = f"{u.caption}. {u.content}"
                yield from cls.find_statute_in_unit(text, u.id, pk)
            elif u.content:
                yield from cls.find_statute_in_unit(u.content, u.id, pk)
            if u.units:
                yield from cls.extract_units(pk, u.units)

    @classmethod
    def get_statutes_from_references(cls, c: Connection) -> Iterator[dict]:
        """Extract relevant statute category and identifier pairs
        from the cls.__tablename__."""
        for row in c.db.execute_returning_dicts(
            corpus_sqlenv.get_template(
                "statutes/references/unique_statutes_list.sql"
            ).render(statute_references_tbl=cls.__tablename__)
        ):
            yield StatuteBase(**row).dict()

    @classmethod
    def update_statute_ids(cls, c: Connection) -> sqlite3.Cursor:
        """Since all statutes present in `db`, supply `matching_statute_id` in
        the references table."""
        with c.session as cur:
            return cur.execute(
                corpus_sqlenv.get_template("statutes/update_id.sql").render(
                    statute_tbl=StatuteRow.__tablename__,
                    target_tbl=cls.__tablename__,
                    target_col=cls.__fields__["matching_statute_id"].name,
                )
            )


class Statute(Integrator):
    id: str
    emails: list[EmailStr]
    meta: StatuteRow
    titles: list[StatuteTitleRow]
    tree: list[StatuteUnit]
    unit_fts: list[StatuteUnitSearch]
    material_paths: list[StatuteMaterialPath]
    statutes_found: list[StatuteFoundInUnit]

    @property
    def relations(self):
        return [
            (StatuteMaterialPath, self.material_paths),
            (StatuteUnitSearch, self.unit_fts),
            (StatuteTitleRow, self.titles),
            (StatuteFoundInUnit, self.statutes_found),
        ]

    @classmethod
    def from_page(cls, details_path: Path):
        # build and validate metadata from the path
        page = StatutePage.build(details_path)

        # assign row for creation
        meta = StatuteRow(**page.dict(exclude={"emails", "tree", "titles"}))

        # setup associated titles
        titles = [
            StatuteTitleRow(**statute_title.dict())
            for statute_title in page.titles
        ]

        # enable full text searches of contents of the tree; starts with `1.1.`
        fts = [
            StatuteUnitSearch(**unit)
            for unit in StatuteUnit.searchables(page.id, page.tree)
        ]

        # full text searches should includes a title row, i.e. node `1.``
        root_fts = [
            StatuteUnitSearch(
                statute_id=page.id,
                material_path="1.",
                unit_text=", ".join(
                    [f"{meta.statute_category} {meta.statute_serial_id}"]
                    + [t.text for t in titles]
                ),
            )
        ]

        return Statute(
            id=page.id,
            emails=page.emails,
            meta=meta,
            tree=page.tree,
            titles=titles,
            unit_fts=root_fts + fts,
            material_paths=[
                StatuteMaterialPath(**unit)
                for unit in StatuteUnit.granularize(
                    pk=page.id, nodes=page.tree
                )
            ],
            statutes_found=list(
                StatuteFoundInUnit.extract_units(pk=page.id, units=page.tree)
            ),
        )

    @classmethod
    def create_via_catid(cls, c: Connection, cat: str, id: str):
        """Create statute/s if the `cat` and `id` passed does not yet
        exist in the `statutes` table of the database."""
        if StatuteRow.get_id_via_catid(c, cat, id):
            return
        rule = Rule(cat=StatuteSerialCategory(cat), id=id)
        for folder in rule.extract_folders(STATUTE_PATH):
            obj = cls.from_page(folder / "details.yaml")
            idx = obj.insert_objects(c, StatuteRow, obj.relations)
            if idx:
                logger.debug(f"Added statute (cat/id): {idx}")

    @classmethod
    def make_tables(cls, c: Connection):
        """The bulk of the fields declared within the Statute
        container are table structures."""
        c.create_table(StatuteRow)  # corresponds to StatutePage
        c.create_table(StatuteTitleRow)  # corresponds to StatuteTitle
        c.create_table(StatuteUnitSearch)
        c.create_table(StatuteMaterialPath)
        c.create_table(StatuteFoundInUnit)
        c.db.index_foreign_keys()

    @classmethod
    def add_rows(cls, c: Connection):
        for detail in STATUTE_FILES:
            cat = detail.parent.parent.stem
            serial = detail.parent.stem
            try:
                obj = cls.from_page(detail)
                obj.insert_objects(c, StatuteRow, obj.relations)
                logger.debug(f"Added statute {cat=} {serial=} from {detail=}")
            except IntegrityError:
                logger.error(f"Already existing; skipped {cat=} {serial=}")
            except ValidationError as e:
                logger.error(f"Validation needed {detail=}; {e=}")
            except Exception as e:
                logger.error(f"Generic exception on insertion: {e=}")
        StatuteFoundInUnit.update_statute_ids(c)
