# post-inclusions

## Ensure that the Statute table exists

After the inclusion files are created, can now create preliminary tables:

```python
from corpus_x import Statute
from sqlpyd import Connection
c = Connection() # type: ignore
Statute.make_tables(c) # this will create the statutes table first (and it relations) so that the foreign keys created in the inclusions tables will work for StatutesInOpinions
```

## Populate StatuteInOpinion and CitationInOpinion rows

Since we have a StatuteInOpinion table and a CitationInOpinion, we can create the same:

```python
from corpus_x import Inclusion
from sqlpyd import Connection
c = Connection() # type: ignore
Inclusion.make_tables(c)
```

These tables reference foreign keys. But since we've already created the Statute table above and the Decision rows are presumed to already exist (and even be populated at this point, see instructions in `corpus-base`), table creation will not result in errors. We can now proceed to insert rows to these tables from the inclusion files we've created above.

```python
from corpus_x import Inclusion
Inclusion.from_files_to_db(c) # glob paths to inclusion.yaml, eta: ~4min.
```

## Included statutes in opinions

We can get the most popular statutes as sourced from decisions already in the database:

```python
from corpus_x import StatuteInOpinion
StatuteInOpinion.most_popular(c)
```

With this list of about ~500 statutes, we can add statutes via their local paths, i.e. using `StatuteInOpinion.add_statutes()`, we'll insert rows in the already created `lex_tbl_statutes`. Each statute row will naturally have primary key `id`; since this is the appropriate foreign key to include in `lex_tbl_opinion_statutes`, we can update the fk to match with `cls.update_statute_ids()`

```python
from corpus_x import StatuteInOpinion
from sqlpyd import Connection
c = Connection() # type: ignore
StatuteInOpinion.add_statutes(c) # eta ~2 minutes to store 500 objects
StatuteInOpinion.update_statute_ids(c)
```

## Included citations / decisions in opinions

We can get the most popular citations as sourced from decisions already in the database:

```python
from corpus_x import CitationInOpinion
CitationInOpinion.most_popular(c)
```

The Decision rows are already inserted so that we can update the included Decision in each CitationInOpinion row:

```python
CitationInOpinion.update_decision_ids(c)
```

## Codifications

Each codification has correlated tables but the whole process can be executed, viz.:

```python
Codification.make_tables(c)
Codification.add_rows(c)
```
