# corpus-x

## Concept

*corpus-pax* + *corpus-base* +  *statute-trees* = converts raw `yaml`-based corpus repository to its database variant **corpus-x**; see [details](notebooks/setup.ipynb). After constructing all of the required tables, it becomes possible to [evaluate the raw data](docs/6-db.md) before transforming it for web / app usage.

## Components

The setup process can be broken down into individual components:

Order | Time | Instruction | Docs
:--:|:--:|--:|:--
0 | ~6sec (if with test data) | [corpus-pax](https://github.com/justmars/corpus-pax#read-me) pre-requiste before `corpus-base` can work. |[Setup](docs/1-setup.md)
1 | ~20-40min | [corpus-base](https://github.com/justmars/corpus-base#read-me) pre-requiste before `corpus-x` can work. |[Setup](docs/1-setup.md)
2 | ~120-130min | If inclusion files not yet created, run script to generate. |[Pre-inclusions](docs/2-pre-inclusions.md)
3 | ~10min | Assuming inclusion files are already created, can populate the various tables under `corpus-x` | [Post-inclusions](docs/3-post-inclusions.md)
4 | ~60min | Litestream output db | [Container setup](docs/4-container.md)
5 | ~10min | Datasette docker container on fly.io | [Remote deployment](docs/5-remote.md)
