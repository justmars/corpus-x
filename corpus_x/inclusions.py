import sqlite3
from collections.abc import Iterator
from typing import NamedTuple

import yaml
from citation_utils import Citation
from corpus_base import DECISION_PATH, CitationRow, DecisionRow, OpinionRow
from loguru import logger
from pydantic import Field
from rich.progress import track
from sqlpyd import Connection, TableConfig
from statute_patterns import Rule, StatuteSerialCategory, count_rules
from statute_patterns.components.utils import DETAILS_FILE
from statute_trees.resources import StatuteBase

from .resources import INCLUSION_FILE, STATUTE_PATH, corpus_sqlenv
from .statutes import StatuteRow


class StatuteInOpinion(StatuteBase, TableConfig):
    __prefix__ = "lex"
    __tablename__ = "opinion_statutes"
    __indexes__ = [["statute_category", "statute_serial_id"]]
    opinion_id: str = Field(..., col=str, fk=(OpinionRow.__tablename__, "id"))
    included_statute_id: str | None = Field(
        None,
        description=(
            "This will be initially absent but"
            "will be updateable through a later update process."
        ),
        col=str,
        fk=(StatuteRow.__tablename__, "id"),
    )  # note difference of statute_id contained here vs statutes.StatuteFK
    mentions: int = Field(
        description=(
            "Each opinion can contain a list of statutes"
            " and their corresponding number."
        ),
        col=int,
    )

    @classmethod
    def extracted(cls, op_id: str, text: str) -> Iterator["StatuteInOpinion"]:
        try:
            for counted in count_rules(text):
                yield cls(
                    opinion_id=op_id,
                    statute_category=StatuteSerialCategory(counted["cat"]),
                    statute_serial_id=counted["id"],
                    mentions=counted["mentions"],
                    included_statute_id=None,
                )
        except Exception as e:
            logger.error(f"Bad statute detection; {op_id=}; {e=}")

    @classmethod
    def most_popular(cls, c: Connection) -> list[dict]:
        """Get a list of unique statutes included during
        `Inclusion.insert_objs_to_db()` and order them according to
        their popularity."""
        template_name = "decisions/inclusions/popular_statutes.sql"
        template = corpus_sqlenv.get_template(template_name)
        return c.db.execute_returning_dicts(
            template.render(op_stat_tbl=cls.__tablename__)
        )

    @classmethod
    def update_statute_ids(cls, c: Connection) -> list[dict]:
        """Assuming proper inserts of missing statutes from
        cls.add_statutes(), update the rows with their proper foreign keys."""
        return c.db.execute(
            corpus_sqlenv.get_template("statutes/update_id.sql").render(
                statute_tbl=StatuteRow.__tablename__,
                target_tbl=cls.__tablename__,
                target_col=cls.__fields__["included_statute_id"].name,
            )
        )

    @classmethod
    def add_statutes(cls, c: Connection):
        """When `Inclusion.from_files_to_db()` first creates StatuteInOpinion
        rows, these rows do not include a `statute_id` (see `opinion_statutes`
        table).

        This function adds statutes to the database from the local repository
        based on the "most popular" StatuteInOpinion rows; since the
        statute_ids now exist, they can be referenced.
        """
        from corpus_x import Statute

        for i in StatuteInOpinion.most_popular(c):
            rule = Rule(cat=StatuteSerialCategory(i["cat"]), id=i["idx"])
            for folder in rule.extract_folders(STATUTE_PATH):
                content_file = folder / DETAILS_FILE
                detail = Rule.get_details(content_file)
                if not detail:
                    logger.error(f"Could not extract detail; {folder=}")
                    continue
                try:
                    obj = Statute.from_page(content_file)
                    idx = obj.insert_objects(c, StatuteRow, obj.relations)
                    if idx:
                        logger.debug(f"Created statute: {idx}")
                except Exception as e:
                    logger.error(f"Did not make statute {content_file=}; {e=}")
                    continue


class CitationInOpinion(Citation, TableConfig):
    __prefix__ = "lex"
    __tablename__ = "opinion_citations"
    __indexes__ = [
        ["included_decision_id", "scra"],
        ["included_decision_id", "phil"],
        ["included_decision_id", "docket"],
        ["included_decision_id", "offg"],
    ]
    opinion_id: str = Field(..., col=str, fk=(OpinionRow.__tablename__, "id"))
    included_decision_id: str | None = Field(
        None,
        description=(
            "This will be initially absent but will be"
            " updateable through a later update process."
        ),
        col=str,
        fk=(DecisionRow.__tablename__, "id"),
    )

    @classmethod
    def extracted(cls, op_id: str, text: str) -> Iterator["CitationInOpinion"]:
        try:
            base = dict(opinion_id=op_id, included_decision_id=None)
            for cite in Citation.extract_citations(text):
                data: dict = cite.dict()
                res = data | base
                yield cls(**res)  # type: ignore
        except Exception as e:
            logger.error(f"Bad citations; {op_id=}; {e=}")

    @classmethod
    def most_popular(cls, c: Connection) -> list[dict]:
        """Get a list of unique citations included during
        `Inclusion.insert_objs_to_db()` and order them
        according to their popularity.
        """
        template_name = "decisions/inclusions/popular_citations.sql"
        template = corpus_sqlenv.get_template(template_name)
        return c.db.execute_returning_dicts(
            template.render(
                cite_tbl=CitationRow.__tablename__,
                op_cite_tbl=cls.__tablename__,
            )
        )

    @classmethod
    def update_decision_ids(cls, c: Connection) -> sqlite3.Cursor:
        """When CitationInOpinions rows are first added by
        `Inclusion.insert_objs_to_db()`, they lack a decision.
        Since the Decision IDs already exist, can update the
        CitationInOpinion rows.
        """
        template_name = "decisions/inclusions/update_decision_id.sql"
        template = corpus_sqlenv.get_template(template_name)
        return c.db.execute(
            template.render(
                cite_tbl=CitationRow.__tablename__,
                target_tbl=cls.__tablename__,
                target_col=cls.__fields__["included_decision_id"].name,
            )
        )


class Inclusion(NamedTuple):
    """Is not necessary as a table since this is used as a namespace to
    collect related entries and consolidating them into separate files.
    """

    source: str  # whether sc / legacy
    origin: str  # identifying folder
    decision_id: str  # source of the opinion
    opinion_id: str  # source of the text
    text: str  # text to examine
    statutes: list[StatuteInOpinion]
    citations: list[CitationInOpinion]

    @classmethod
    def get_base_data(cls, c: Connection, pk: str) -> dict:
        sql_file = "decisions/get_base.sql"
        template = corpus_sqlenv.get_template(sql_file)
        results = c.db.execute_returning_dicts(
            template.render(
                target_decision_id=pk,
                decision_tbl=DecisionRow.__tablename__,
            )
        )
        if results:
            return results[0]
        return {}

    @classmethod
    def list_opinions_of_decision(cls, c: Connection, pk: str) -> dict:
        sql_file = "decisions/list_opinions_of_decision.sql"
        template = corpus_sqlenv.get_template(sql_file)
        results = c.db.execute_returning_dicts(
            template.render(
                target_decision_id=pk,
                opinion_tbl=OpinionRow.__tablename__,
                op_cite_tbl=CitationInOpinion.__tablename__,
                decision_tbl=DecisionRow.__tablename__,
                op_stat_tbl=StatuteInOpinion.__tablename__,
                statute_tbl=StatuteRow.__tablename__,
            )
        )
        if results:
            return results[0]
        return {}

    @classmethod
    def make_tables(cls, c: Connection):
        """These tables reference foreign keys.

        Presumed to already exist:

        1. Statute table
        2. Decision table

        Args:
            c (Connection): sqlpyd connection to the database
        """
        if c.table(StatuteRow):
            c.create_table(StatuteInOpinion)
        if c.table(DecisionRow):
            c.create_table(CitationInOpinion)

    @property
    def content_for_file(self):
        msg = f"Inclusions detected in {self.path_to_folder=}"
        statutes = [i.dict(exclude_none=True) for i in self.statutes]
        citations = [i.dict(exclude_none=True) for i in self.citations]
        if not statutes and not citations:
            logger.debug(f"No {msg.lower()}")
            return
        else:
            logger.debug(msg)
            return {"statutes": statutes, "citations": citations}

    @property
    def path_to_folder(self):
        folder = DECISION_PATH / self.source / self.origin
        if not folder.exists():
            logger.error(f"Bad {folder=} stored in the database.")
        return folder


def populate_db_with_inclusions(c: Connection):
    """Assuming that `create_inclusion_files_from_db_opinions()` has
    previously run, we can extract the contents of each file and insert
    them into the database.
    """
    paths = DECISION_PATH.glob(f"**/{INCLUSION_FILE}")
    for path in track(paths, description="Pull inclusions..."):
        obj = yaml.safe_load(path.read_bytes())
        if obj.get("statutes"):
            c.add_records(StatuteInOpinion, obj["statutes"])
        if obj.get("citations"):
            c.add_records(CitationInOpinion, obj["citations"])


def create_inclusion_files_from_db_opinions(c: Connection):
    """Need a connection to the database to retrieve Opinion objects.

    From the text found in each opinion, extract statutes and citations
    and save to an inclusion file.

    The inclusion file shall be stored in in the same source
    repository (see source / origin fields)."""

    def read_opinions(c: Connection) -> list[dict[str, str]]:
        """Join each opinion of each decision together to collect
        all opinions in the database.

        Each collected entry will consist of:

        1. `source` and `origin` to help with the getting the local path.
        2. `decision_id` and `opinion_id` to create the resulting record.
        3. `text` of the opinion which will be used to determine inclusions.
        """
        sql_file = "decisions/inclusions/read_opinions.sql"
        return c.db.execute_returning_dicts(
            corpus_sqlenv.get_template(sql_file).render(
                opinion_tbl=OpinionRow.__tablename__,
                decision_tbl=DecisionRow.__tablename__,
            )
        )

    def set_inclusion_objects(rows: list[dict]):
        """An `Inclusion` instance is a NamedTuple which consists of
        included statutes and decisions from an opinion's text.
        This function helps extract such "inclusions"."""
        for o in track(rows, description="Set inclusions..."):
            obj = Inclusion(
                **o,
                statutes=list(
                    StatuteInOpinion.extracted(
                        op_id=o["opinion_id"],
                        text=o["text"],
                    )
                ),
                citations=list(
                    CitationInOpinion.extracted(
                        op_id=o["opinion_id"],
                        text=o["text"],
                    )
                ),
            )
            if obj.content_for_file:
                yield obj

    opinions: list[dict] = read_opinions(c)
    inclusions: Iterator[Inclusion] = set_inclusion_objects(opinions)
    for obj in inclusions:
        logger.debug(f"Creating {obj.source=} / {obj.origin=}")
        f = DECISION_PATH / obj.source / obj.origin / INCLUSION_FILE
        f.unlink(missing_ok=True)  # replace
        with open(f, "w") as writefile:
            yaml.safe_dump(obj.content_for_file, writefile)


def set_inclusions(c: Connection):
    """Collect the pre-processed data and insert the same
    into the created database tables.

    Estimate at the end of 2022 (factors to consider):

    1. the last time data was scraped as raw files,
    2. the time separate opinions were manually included

    Note: the statute and inclusion tables need to be created
    before the pre-processed data can be inserted.

    Result:

    As of end of 2022:

    table | row count | purpose
    --:|:-- |:--
    `CitationsInOpinions` | ~484k | itemize citations found per opinion
    `StatutesInOpinions` | ~99k  | itemize statutes found per opinion

    After `populate_db_with_inclusions` is run, what will
    exists in the database are records of statutes / citations but not
    the statute_ids / decision_ids themselves. See `purpose` noted above
    for the citations and statutes found per opinion.

    Recall that the inclusion files are created because of `corpus-base`
    tables. At the time the `corpus-base` tables were created, there were
    were no StatuteInOpinions and CitationInOpinions tables yet since
    these only exist in `corpus-x`

    An update will need to be made so that these tables get a foreign key
    to their proper tables.

    Args:
        c (Connection): sqlpyd connection to the database
    """
    populate_db_with_inclusions(c)
    StatuteInOpinion.update_statute_ids(c)
    CitationInOpinion.update_decision_ids(c)
    c.db.index_foreign_keys()
