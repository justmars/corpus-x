# pre-inclusions

## concept

Each opinion declared via `corpus_base` will contain references to:

1. statutes;
2. citations; and
3. segments.

We'll use these references by first generating an inclusion `yaml` file for each opinion to serve as future rows to `corpus_x`-related tables:

1. `opinion_statutes`
2. `opinion_citations`
3. `opinion_segments`

## locate inclusion files

The files will be stored in the same `decision/sc/xxx` or `decision/legacy/xxx` folders previously setup by `corpus_base`.

```python
>>> from corpus_base.utils import DECISION_PATH
>>> DECISION_PATH
PosixPath(path-to/decisions/)
```

## set inclusion files

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

## pull files

After inclusion files are created, we can load the referenced data to the database:

```python shell
>>> from corpus_x.inclusions import populate_db_with_inclusions
>>> populate_db_with_inclusions(c) # takes about ~30 minutes
```

## resulting database

As of end of 2022:

table | row count
--:|:--
`CitationsInOpinions` | ~484k
`StatutesInOpinions` | ~99k
`SegmentRow` | [~700k]

## segment discovery

The [segmenting function](../corpus_x/utils/segmentize.py) determines the kind of rows that becomes associated with an opinion and a decision.

### search for qualifying segments

The `char_count` can be used to limit the number of segments:

```sql
select count(id)
from sc_tbl_segments
where char_count >= 500
```

`char_count` is the SQL column per segment.

### limit input of segments

`MIN_LENGTH_CHARS_IN_LINE` is the python filtering mechanism that determines what goes into the database. Assuming a minimum of only 20 characters, the number of segment rows can be as many as ~2.9m.

`MIN_LENGTH_CHARS_IN_LINE` | Total Num. of Rows | Time to Create from Scratch
:--:|:--:|:--:
20 | ~2.9m | 1.5 hours
500 | ~700k | 40 minutes
1000 | ~170k | TBD

We will settle with `500` until we come up with a better segmentizing algorithm.

### number of segments per decision

```sql
select decision_id, count(id)
from sc_tbl_segments
where char_count >= 500
group by decision_id
```
