# corpus-x

*corpus-pax* + *corpus-base* + *statute-trees* = converts raw `yaml`-based corpus repository to its database variant **corpus-x**; see [details](notebooks/setup.ipynb). After constructing all of the required tables, it becomes possible to [evaluate the raw data](docs/5-db-evaluate.md) before transforming it for web / app usage.

Order | Time | Instruction | Docs
:--:|:--:|--:|:--
0 | ~6sec (if with test data) | [corpus-pax](https://github.com/justmars/corpus-pax#read-me) pre-requiste before `corpus-base` can work. |[Setup](docs/1-setup.md)
1 | ~20-40min | [corpus-base](https://github.com/justmars/corpus-base#read-me) pre-requiste before `corpus-x` can work. |[Setup](docs/1-setup.md)
2 | ~120-130min | If inclusion files not yet created, run script to generate. |[Pre-inclusions](docs/2-pre-inclusions.md)
3 | ~10min | Assuming inclusion files are already created, can populate the various tables under `corpus-x` | [Post-inclusions](docs/3-post-inclusions.md)
4 | ~60min | Litestream output `x.db` on AWS bucket | [Replicated db](docs/4-aws-replicate.md)

## things to know when updating content

The event data contained in the `units` field of the codification need to be updated separately.
