import abc
from pathlib import Path
from typing import Any

from corpus_pax import Individual
from jinja2 import Environment, PackageLoader, select_autoescape
from pydantic import BaseModel, EmailStr
from sqlpyd import Connection

BASE = "code/corpus"
"""Source of all local files"""

STATUTE_PATH = Path().home().joinpath(f"{BASE}/statutes")
STATUTE_FILES = STATUTE_PATH.glob("**/*/details.yaml")

CODIFICATION_PATH = Path().home().joinpath(f"{BASE}/codifications")
CODIFICATION_FILES = CODIFICATION_PATH.glob("**/*.yaml")

DOCUMENT_PATH = Path().home().joinpath(f"{BASE}/documents")
DOCUMENT_FILES = DOCUMENT_PATH.glob("**/*.yaml")

INCLUSION_FILE = "inclusions.yaml"
"""Name of the file that will host all the included components of a decision"""


corpus_sqlenv = Environment(
    loader=PackageLoader(package_name="corpus_x", package_path="sql"),
    autoescape=select_autoescape(),
)


class Integrator(BaseModel, abc.ABC):
    """
    Each Integrator class ensures that inheriting classes implement:

    1. common fields: `id`, `emails`, `meta`, `tree`, and `unit_fts`
    2. `make_tables()`: create the model's instances in the sqlite db
    3. `add_rows()`: to populate the tables created
    4. `from_page()`: given a raw yaml file, extract fields into the BaseModel
    5. `@relations`: the BaseModel will have relationships to other BaseModels

    The reason for requiring `emails` is that the common
    `insert_objects()` function can: create an m2m table with respect
    to authors

    The reason for requiring `@relations` is that the common
    `insert_objects()` function can: go through each of the tuples where in
    the first item of the tuple represents a table and the second item of the
    tuple, rows to be inserted in such a table.
    """

    id: str = NotImplemented
    emails: list[EmailStr] = NotImplemented
    meta: Any = NotImplemented
    tree: list[Any] = NotImplemented
    unit_fts: list[Any] = NotImplemented

    @classmethod
    @abc.abstractmethod
    def make_tables(cls, c: Connection) -> None:
        """Common process for creatng the tables associated
        with the concrete class."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def add_rows(cls, c: Connection) -> None:
        """Common process for creating objects from the source
        files for these to become prospective rows to
        the tables created."""
        raise NotImplementedError

    @classmethod
    @abc.abstractmethod
    def from_page(cls, file_path: Path) -> None:
        """The `file_path` expects an appropriate .yaml file
        containing the metadata. The data will be processed into an
        interim 'page' that will eventually build an instance of
        the concrete class."""
        raise NotImplementedError

    @property
    @abc.abstractmethod
    def relations(cls):
        """Helper property to associate TableConfigured models
        to their instantiated values in preparation for
        database insertion."""
        raise NotImplementedError

    def insert_objects(
        self,
        c: Connection,
        obj: Any,
        correlations: list[tuple[Any, Any]],
    ) -> str:
        """The use of the concrete class' `insert_objects()` function
        implies that an `Individual` table already exists.

        The `obj` is a subclass of `TableConfig`. Since we're already aware
        of the `id` of the `obj`, we can also use this same id to create the
        author of the object as well as the correlated entities.

        Each correlated entity must also be a subclass of `TableConfig`.
        """
        record = self.meta.dict(exclude={"emails"})
        c.add_record(obj, record)

        for email in self.emails:
            c.table(obj).update(self.id).m2m(
                other_table=c.table(Individual),
                lookup={"email": email},
                pk="id",
            )

        for related in correlations:
            c.add_cleaned_records(
                related[0],  # the related model which must be
                related[1],  # the instance of the object
            )

        return self.id


def sql_get_detail(generic_tbl_name: str, generic_id: str) -> str:
    return corpus_sqlenv.get_template("base/get_detail.sql").render(
        generic_tbl=generic_tbl_name,
        target_id=generic_id,
    )


def sql_get_authors(generic_tbl_name: str, generic_id: str) -> str:
    """Produce the SQL query string necessary to get the authors from the
    Individual table based on the `generic_tbl_name`'s target `generic_id`.

    Each generic_tbl_name will be sourced from either: DecisionRow,
    CodeRow, DocRow, StatuteRow. Each of these tables are associated
    with the Individual table. The result looks something like this:

    ```
    >>> from .statutes import StatuteRow
    >>> sql = sql_get_authors(StatuteRow.__tablename__, "ra-386-june-18-1949")
    >>> type(sql)
    <class 'str'>
    ```

    See sqlite_utils which creates m2m object tables after sorting the tables
    alphabetically.
    """
    tables = [generic_tbl_name, Individual.__tablename__]
    template = corpus_sqlenv.get_template("base/get_author_ids.sql")
    return template.render(
        generic_tbl="_".join(sorted(tables)),
        col_generic_obj="_".join([generic_tbl_name, "id"]),
        col_author_id="_".join([Individual.__tablename__, "id"]),
        target_id=generic_id,
    )


def get_authored_object(
    c: Connection, generic_tbl_name: str, generic_id: str
) -> dict:
    tbl = generic_tbl_name
    idx = generic_id
    a = c.db.execute_returning_dicts(sql_get_detail(tbl, idx))[0]
    b = c.db.execute_returning_dicts(sql_get_authors(tbl, idx))[0]
    result = a | b
    return result
