# Statutes

## Statute path/s

All statutes are sourced from a parent `/statutes`

Each child folder of the parent is a category /statutes/`ra`, /statutes/`roc`, etc

Each child folder of a category is the *identifier* of the statute so in cases where variants are employed, can distinguish
via a suffix integer, e.g. statutes/am/`00-5-03-sc-1` and  statutes/am/`00-5-03-sc-2`.

## Statute creation and population

It takes about **15 minutes** to populate all the statute tables.

```py
>>> from corpus_x.statutes import Statute, StatuteFoundInUnit, Connection
>>> c = Connection(DatabasePath="x.db", WAL=True)
>>> Statute.make_tables(c)
>>> Statute.add_rows(c)
>>> StatuteFoundInUnit.update_statute_ids(c)
<sqlite3.Cursor object at 0x10ca544d0>
```
