
# Decision inclusions

## Concept of inclusions

Each opinion declared via `corpus_base` will contain references to:

1. statutes;
2. citations

We'll use these references by first generating an inclusion `yaml` file for each opinion to serve as future rows to `corpus_x`-related tables:

1. `opinion_statutes`
2. `opinion_citations`

## Inclusion path/s

All decisions are sourced from a parent `/decisions`

Each child folder of the parent is one of 2 categories: (1) /decisions/`sc` and (2) /decisions/`legacy`

Each child folder of a category is a decision identifier, e.g. decisions/sc/`1234`; it contains a decision's content.

The inclusion file for each decision will be stored in this identifier folder.

## Creation of inclusion files

### Populate local files

```py
>>> from sqlpyd import Connection
>>> c = Connection(DatabasePath='x.db', WAL=True) # assuming x.db is the file
>>> from corpus_x.inclusions import create_inclusion_files_from_db_opinions
>>> create_inclusion_files_from_db_opinions(c) # will use sc_tbl_opinions
# Set inclusions... ━━━━━━╺━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━  16% 1:10:21
```

It takes **~60-90 minutes** to parse through **60k** long form pieces of text.

Note: it used to take 6 hours; the optimization of the codebase via `statute-patterns` has significantly cut down on the time.

This process should be called whenever here is change in the opinions table.

### Pull from local files to database

We can now proceed to insert rows from the `inclusion.yaml` file to the proper tables.

It takes about **~20 minutes** to populate all the inclusion tables.

```py
>>> from corpus_x import Inclusion
>>> Inclusion.from_files_to_db(c)
>>> StatuteInOpinion.add_statutes(c)  # eta ~2 minutes to store 500 objects
>>> StatuteInOpinion.update_statute_ids(c)
>>> CitationInOpinion.update_decision_ids(c)
```
