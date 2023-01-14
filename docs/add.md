# add to db

## statutes

### statute path/s

All statutes are sourced from a parent `/statutes`

Each child folder of the parent is a category /statutes/`ra`, /statutes/`roc`, etc

Each child folder of a category is the *identifier* of the statute so in cases where variants are employed, can distinguish
via a suffix integer, e.g. statutes/am/`00-5-03-sc-1` and  statutes/am/`00-5-03-sc-2`.

### statute creation and population

It takes about **15 minutes** to populate all the statute tables.

```python shell
>>> from corpus_x.statutes import Statute, StatuteFoundInUnit, Connection
>>> c = Connection(DatabasePath="x.db", WAL=True)
>>> Statute.make_tables(c)
>>> Statute.add_rows(c)
>>> StatuteFoundInUnit.update_statute_ids(c)
<sqlite3.Cursor object at 0x10ca544d0>
```

## codifications

### codification path/s

All codifications are sourced from a parent `/codifications`

Each child folder of the parent is a category /codifications/`ra`, /codifications/`roc`, etc

Each child folder of a category is the *serial id* of such category, e.g. /codifications/ra/`386`

Each file in the latter folder is named after its identifier, e.g. `mv-civil-v1.yaml`

### codification creation and population

It takes about **~3 minutes** to populate all the codification tables.

```python shell
>>> from corpus_x.statutes import Codification, CodeRow, Connection
>>> c = Connection(DatabasePath="x.db", WAL=True)
>>> Codification.make_tables(c)
>>> Codification.add_rows(c)
[
    'mv-2022-pd-603-modern-child-and-youth-welfare-code-v1',
    'mv-2022-pd-612-modern-insurance-code-v1',
    'mv-2022-pd-442-labor-code-of-the-philippines-v1',
    'mv-2022-bp-129-judiciary-reorganization-act-v1',
    'mv-2022-ca-146-modern-public-service-act-v1',
    'mv-2022-act-3815-revised-penal-code-of-the-philippines-v1',
    'mv-2022-ra-7160-local-government-code-v1',
    'mv-2022-ra-8491-modern-flag-code-v1',
    'mv-2022-ra-8293-intellectual-property-code-v1',
    'mv-2022-ra-7610-child-abuse-act-v1',
    'mv-2022-ra-11232-revised-corporation-code-of-the-philippines-v1',
    'mv-2022-ra-8424-the-tax-code-v1',
    'mv-2022-ra-9160-anti-money-laundering-act-v1',
    'mv-2022-ra-9485-modern-anti-red-tape-act-v1',
    'mv-2022-ra-8550-fisheries-code-v1',
    'mv-2022-ra-9344-juvenile-justice-and-welfare-act-of-2006-v1',
    'mv-2022-ra-7042-modern-foreign-investments-acts-v1',
    'mv-2022-ra-9165-comprehensive-dangerous-drugs-act-of-2002-v1',
    'mv-2022-ra-386-modern-civil-code-v1',
    'mv-2022-const-1987-the-1987-constitution-of-the-philippines-v1',
    'mv-2022-rule-am-19-10-20-sc-revised-rules-of-civil-procedure-v1',
    'mv-2022-rule-am-19-08-15-sc-revised-rules-on-evidence-roc-v1',
    'mv-2022-rule-am-00-5-03-sc-revised-rules-of-criminal-procedure-roc-v1',
    'mv-2022-roc-1964-special-proceedings-roc-v1',
    'mv-2022-roc-1964-legal-and-judicial-ethics-roc-v1',
    'mv-2022-eo-292-the-administrative-code-v1',
    'mv-2022-eo-209-the-family-code-of-the-philippines-v1'
]
```

## decision inclusions

### inclusion path/s

All decisions are sourced from a parent `/decisions`

Each child folder of the parent is one of 2 categories: (1) /decisions/`sc` and (2) /decisions/`legacy`

Each child folder of a category is a container for a decision file which will be populated with an `inclusion.yaml` file.

### creation inclusion file

### populate

```python shell
>>> from sqlpyd import Connection
>>> c = Connection(DatabasePath='x.db', WAL=True) # assuming x.db is the file
>>> from corpus_x.inclusions import create_inclusion_files_from_db_opinions
>>> create_inclusion_files_from_db_opinions(c) # will use sc_tbl_opinions
# Set inclusions... ━━━━━━╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  16% 1:10:21
```

It takes **~60-90 minutes** to parse through **60k** long form pieces of text.

Note: it used to take 6 hours; the optimization of the codebase via `statute-patterns` has significantly cut down on the time.

This process should be called whenever here is change in the opinions table.

### pull

We can now proceed to insert rows from the `inclusion.yaml` file to the proper tables.

It takes about **~20 minutes** to populate all the inclusion tables.

```python shell
>>> from corpus_x import Inclusion
>>> Inclusion.from_files_to_db(c)
>>> StatuteInOpinion.add_statutes(c)  # eta ~2 minutes to store 500 objects
>>> StatuteInOpinion.update_statute_ids(c)
>>> CitationInOpinion.update_decision_ids(c)
```
