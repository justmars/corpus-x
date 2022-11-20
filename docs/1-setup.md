# presetup

## db

Establish the sqlite3 database connection within the current working directory:

```python
from sqlpyd import Connection
c = Connection(DatabasePath="x.db", WAL=True) # type: ignore
```

## pax

Create individuals / organizations tables; individuals will be formatters of decisions, statutes, etc.:

```python
from corpus_pax import init_persons
init_persons(c) # creates the tables and populates the same; eta: ~9sec.
```

## sc

Create decision and opinion tables; this will be the source of getting most popular statutes and citations for decision inclusions. This assumes that a local repository has already been downloaded that will serve as the source for creating the table rows.

Note that this creates an entryin `logs/base.log` highlighting recurring errors, e.g.

- Multiple ids for a ponente writer
- No ids for a ponente writer
- Duplicate entry of decision ids

```python
from corpus_base import build_sc_tables, init_sc_cases
build_sc_tables(c) # creates tables
init_sc_cases(c) # populates the tables created; eta: ~17min.
```

## x

With the previous tables existing, can now create the remaining tables since their foreign keys will be "referenceable":

```python
from corpus_x import build_x_tables
build_x_tables(c) # creates tables
```
