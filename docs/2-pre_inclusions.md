# pre-inclusions

## concept

Each opinion declared via `corpus_base` will contain references to statutes and citations. We'll use these references by first generating an inclusion `yaml` file for each opinion to serve as future rows to 2 `corpus_base`-related tables: `opinion_statutes` and `opinion_citations`.

## storage

The files will be stored in the same `decision/sc/xxx` or `decision/legacy/xxx` folders previously setup by `corpus_base`.

```python
>>> from corpus_base.utils import DECISION_PATH
>>> DECISION_PATH
PosixPath(path-to/decisions/)
```

## call

```python
>>> Inclusion.save_obj_to_files(c) # check the individual folders of DECISION_PATH after 30 min.
```

It takes **~60 minutes** to parse through **60k** long form pieces of text. (Note: it used to take 6 hours; the optimization of the codebase via `statute-patterns` has significantly cut down on the time.) Enabling this one-time process makes it easier to load the references to the database after they've been collected.

## process

```python
>>> extracts = Inclusion.extractor(c)
>>> extracted = next(extracts)
>>> extracted # this is a NamedTuple
Inclusion(
    source='sc',
    origin='38254',
    decision_id='38254',
    opinion_id='38254-main',
    text='# Ponencia\n\nHerein appellant x x x ', # full text excluded
    statutes=[
        StatuteInOpinion(
            statute_category='ra',
            statute_serial_id='7659',
            opinion_id='38254-main',
            mentions=2
        ),
        StatuteInOpinion(
            statute_category='ra',
            statute_serial_id='4111',
            opinion_id='38254-main',
            mentions=1
        ),
        StatuteInOpinion(
            statute_category='act',
            statute_serial_id='3815',
            opinion_id='38254-main',
            mentions=1
        )
    ],
    citations=[
        CitationInOpinion(
            docket='GR 126134, Mar. 02, 1999',
            docket_category='GR',
            docket_serial='126134',
            docket_date=datetime.date(1999, 3, 2),
            phil=None,
            scra=None,
            offg=None,
            opinion_id='38254-main'
        ),
        CitationInOpinion(
            docket='GR 128619-21, Dec. 17, 1998',
            docket_category='GR',
            docket_serial='128619-21',
            docket_date=datetime.date(1998, 12, 17),
            phil=None,
            scra=None,
            offg=None,
            opinion_id='38254-main'
        ), # full list excluded
    ...
    ]
)
>>> extracted.path_to_folder # introspect where the inclusions file will be created
PosixPath('/<local-path-to>/decisions/<source>/<origin>')
>>> extracted.add_file()
>>> extracted.load_inclusions(extracted.path_to_folder) # retrieve data from file
{
    'citations': [
        {
            'docket': 'GR 126134, Mar. 02, 1999',
            'docket_category': 'GR',
            'docket_date': datetime.date(1999, 3, 2),
            'docket_serial': '126134',
            'opinion_id': '38254-main'
        },
        {
            'docket': 'GR 128619-21, Dec. 17, 1998',
            'docket_category': 'GR',
            'docket_date': datetime.date(1998, 12, 17),
            'docket_serial': '128619-21',
            'opinion_id': '38254-main'
        },
        {'opinion_id': '38254-main', 'scra': '281 SCRA 452'},
        {'opinion_id': '38254-main', 'scra': '265 SCRA 668'},
        {'opinion_id': '38254-main', 'scra': '271 SCRA 189'},
        {'opinion_id': '38254-main', 'scra': '262 SCRA 544'},
        {'opinion_id': '38254-main', 'scra': '257 SCRA 658'},
        {'opinion_id': '38254-main', 'scra': '269 SCRA 293'},
        {'opinion_id': '38254-main', 'scra': '269 SCRA 293'},
        {'opinion_id': '38254-main', 'scra': '264 SCRA 425'},
        {'opinion_id': '38254-main', 'scra': '264 SCRA 425'},
        {'opinion_id': '38254-main', 'scra': '259 SCRA 90'}
    ],
    'statutes': [
        {
            'mentions': 1,
            'opinion_id': '38254-main',
            'statute_category': 'ra',
            'statute_serial_id': '4111'
        },
        {
            'mentions': 1,
            'opinion_id': '38254-main',
            'statute_category': 'act',
            'statute_serial_id': '3815'
        },
        {
            'mentions': 2,
            'opinion_id': '38254-main',
            'statute_category': 'ra',
            'statute_serial_id': '7659'
        }
    ]
}
