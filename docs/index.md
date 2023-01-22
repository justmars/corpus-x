# Overview

## Concept

[corpus-pax](https://github.com/justmars/corpus-pax) + [corpus-base](https://github.com/justmars/corpus-base) + [statute-trees](https://github.com/justmars/statute-trees) = converts raw `yaml`-based corpus repository to its database variant **corpus-x**. After constructing all of the required tables, it becomes possible to [evaluate the raw data](evaluation.md)

## Mode

Order | Time | Instruction
:--:|:--:|--:|
1 | ~6sec (if with test data) | [corpus-pax](https://github.com/justmars/corpus-pax#read-me) pre-requiste before `corpus-base` can work.
2 | ~20min | [corpus-base](https://github.com/justmars/corpus-base#read-me) pre-requiste before `corpus-x` can work.
3 | ~70min | If inclusion files not yet created, run script to generate.
4 | ~30min | Assuming inclusion files are already created, can populate the various tables under `corpus-x`
5 | ~40 to ~60min | Litestream local output `x.db` to AWS bucket

## Build from corpus-base

Assuming step 3 above has already been completed as a separate process and `pax_` and `sc_` tables have already been added:

```py
>>> from corpus_x import setup_x
>>> from sqlpyd import Connection
>>> c = Connection(DatabasePath="x.db", WAL=True)
>>> setup_x('x.db') # adds to the database in present working directory, takes ~2300 seconds or ~40 minutes
```

The produced `x.db` file can then be [replicated](replication.md) to aws via litestream, which should take another hour.

## From Local Files to DB

See prior [documentation](https://github.com/justmars/corpus-base) for corpus-base tables.
