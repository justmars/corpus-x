from pathlib import Path

from loguru import logger
from pydantic import Field
from sqlpyd import Connection, TableConfig
from statute_trees import DocPage, DocUnit, Page, generic_content, generic_mp

from .codifications import CodeRow
from .resources import DOCUMENT_PATH, Integrator


class DocRow(Page, TableConfig):
    __prefix__ = "lex"
    __tablename__ = "documents"


class DocUnitSearch(TableConfig):
    __prefix__ = "lex"
    __tablename__ = "document_fts_units"
    __indexes__ = [["document_id", "material_path"]]
    document_id: str = Field(..., col=str, fk=(DocRow.__tablename__, "id"))
    material_path: str = generic_mp
    unit_text: str = generic_content


class Document(Integrator):
    id: str
    meta: DocRow
    tree: list[DocUnit]
    unit_fts: list[DocUnitSearch]

    @property
    def relations(self):
        return [(DocUnitSearch, self.unit_fts)]

    @classmethod
    def make_tables(cls, c: Connection):
        if c.table(CodeRow):
            c.create_table(DocRow)
            c.create_table(DocUnitSearch)

    @classmethod
    def add_rows(cls, c: Connection):
        for f in DOCUMENT_PATH.glob("**/*.yaml"):
            obj = cls.from_page(f)
            idx = obj.insert_objects(c, DocRow, obj.relations)
            logger.debug(f"Added document {idx=} from {f.stem=}")

    @classmethod
    def from_page(cls, file_path: Path):
        page = DocPage.build(file_path)
        if not page:
            raise Exception(f"No page from {file_path=}")
        searachables = DocUnit.searchables(page.id, page.tree)
        return cls(
            id=page.id,
            emails=page.emails,
            meta=DocRow(**page.dict(exclude={"tree", "emails"})),
            tree=page.tree,
            unit_fts=[DocUnitSearch(**unit) for unit in searachables],
        )
