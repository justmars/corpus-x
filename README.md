# corpus-x

## Concept

*corpus-pax* + *corpus-base* +  *statute-trees* = converts raw `yaml`-based corpus repository to its database variant **corpus-x**; see [details](notebooks/setup.ipynb). After constructing all of the required tables, it becomes possible to evaluate the raw data before constructing the same for the web / app usage.

## Components

The setup process can be broken down into individual components:

Order | Time | Instruction | Docs
:--:|:--:|--:|:--
0 | ~6sec (if with test data) | [corpus-pax](https://github.com/justmars/corpus-pax#read-me) pre-requiste before `corpus-base` can work. |[Setup](docs/1-setup.md)
1 | ~20-40min | [corpus-base](https://github.com/justmars/corpus-base#read-me) pre-requiste before `corpus-x` can work. |[Setup](docs/1-setup.md)
2 | ~120-130min | If inclusion files not yet created, run script to generate. |[Pre-inclusions](docs/2-pre_inclusions.md)
3 | ~10min | Assuming inclusion files are already created, can populate the various tables under `corpus-x` | [Post-inclusions](docs/3-post-inclusions.md)
4 | ~60min | Package into Docker container, replicate to litestream | [Container](docs/4-container.md)

## Decision

```python
>>> from sqlpyd import Connection
>>> from corpus_x import get_decision
>>> case_pk = "gr-l-63915-apr-24-1985-136-scra-27-220-phil-422"
>>> case_detail = get_decision(Connection(DatabasePath="x.db"), case_pk)
>>> print(case_detail)
{
    'created': 1662986006.2967641,
    'modified': 1662986006.2967641,
    'title': 'Lorenzo M. Tañada, Abraham F. Sarmiento, and Movement Of Attorneys For Brotherhood, Integrity And Nationalism, Inc.  [MABINI], Petitioners, Vs. Hon. Juan C. Tuvera' x x x,
    'description': 'GR L-63915, Apr. 24, 1985, 136 SCRA 27, 220 Phil. 422',
    'date': '1985-04-24',
    'justice_id': 101,
    'per_curiam': 0,
    'composition': 'En Banc',
    'category': 'Decision',
    'author_list': [{'id': 'mv', 'display': 'Marcelino Veloso III', 'img': 'members-mv'}],
    'opinions_list': [
        {
            'opinion_id': 'c6812-100',
            'title': 'Concurring Opinion',
            'justice_id': 100,
            'text': x x x,
            'statutes': [],
            'unmatched_statutes': [],
            'decisions': [],
            'unmatched_decisions': []
        },
        x x x # different opinions with their respective text and citations
        {
            'opinion_id': 'c6812-main',
            'title': 'Ponencia',
            'justice_id': 101,
            'text': x x x,
            'statutes': [
                {
                    'id': 'ra-386-june-18-1949',
                    'official_title': 'An Act to Ordain and Institute the Civil Code of the Philippines',
                    'serial_title': 'Republic Act No. 386',
                    'statute_date': '1949-06-18'
                }
            ],
            'unmatched_statutes': [{'statute_category': 'ca', 'statute_serial_id': '638'}], # this implies that there is no statute presently existing in the database having the above category and serial id
            'decisions': [ # each decision
                {
                    'id': 'gr-l-52245-jan-22-1980-180-phil-369',
                    'title': 'Patricio Dumlao, Romeo B. Igot, And Alfredo Salapantan, Jr., Petitioners, Vs. Commission On Elections, Respondent.',
                    'description': 'GR L-52245, Jan. 22, 1980, 180 Phil. 369',
                    'date': '1980-01-22'
                },
                x x x # each decision in the opinion can be linked
            ],
            'unmatched_decisions': [
                {'docket': None, 'scra': None, 'phil': '45 Phil. 345', 'offg': None},
                {'docket': None, 'scra': '16 SCRA 151', 'phil': None, 'offg': None},
                {'docket': None, 'scra': '18 SCRA 924', 'phil': None, 'offg': None},
                x x x # this implies that there is no decision presently existing in the database having the citations itemized
            ]
        }
    ]
}
```

## Codification

With respect to a codification_id:

```python
>>> from sqlpyd import Connection
>>> from corpus_x import get_codification
>>> code_pk = "gr-l-63915-apr-24-1985-136-scra-27-220-phil-422"
>>> code_detail = get_codification(Connection(DatabasePath="x.db"), code_pk)
>>> print(code_detail)
{
    'created': 1668327185.4456773,
    'modified': 1668327185.4456773,
    'title': 'Judiciary Reorganization Act',
    'description': 'The most recent statute designating jurisdiction of general courts in the Philippines.\n',
    'date': '2022-10-01',
    'statute_category': 'bp',
    'statute_serial_id': '129',
    'statute_id': 'bp-129-august-14-1981',
    'statute_date': '1981-08-14',
    'statute_titles': [
        {'title': 'The Judiciary Reorganization Act of 1980', 'category': 'short'},
        {'title': 'Batas Pambansa Blg. 129', 'category': 'serial'},
        {
            'title': 'An Act Reorganizing The Judiciary, Appropriating Funds Therefor, And For Other Purposes.',
            'category': 'official'
        } # these are the ways that this statute is referred to
    ],
    'units': [
        { # this is the nested tree that can be styled via html / css / js
            'item': 'Judiciary Reorganization Act',
            'id': '1.', # why necessary to create a root node? easier to create relationships, i.e. repeals / associations of whole documents to a single unit node
            'units': [
                {
                    'item': 'Container 1',
                    'caption': 'Preliminary Chapter',
                    'id': '1.1.',
                    'units': [
                        {
                            'item': 'Section 1',
                            'caption': 'Title.',
                            'content': 'This Act shall be known as "The Judiciary Reorganization Act of 1980."',
                            'id': '1.1.1.',
                            'units': []
                        },
                    ],
                    x x x
                },
                x x x
            ],
        },
        x x x,
    ],
    'author_list': [{'id': 'mv', 'display': 'Marcelino Veloso III', 'img': 'members-mv'}],
    'event_statute_affectors': [
        {
            'id': 'ra-11576-july-30-2021',
            'official_title': 'An Act Further Expanding The Jurisdiction Of The Metropolitan Trial Courts, Municipal Trial Courts In Cities, Municipal Trial Courts, And Municipal Circuit Trial Courts, Amending For The Purpose Batas Pambansa Blg. 129, Otherwise Known As "The Judiciary Reorganization Act Of 1980," As Amended\n',
            'serial_title': 'Republic Act No. 11576',
            'statute_date': '2021-07-30'
        },
        {
            'id': 'ra-11455-august-30-2019',
            'official_title': 'An Act Creating Two (2) Additional Branches Of The Regional Trial Court In The Province Of Sultan Kudarat, One Each To Be Stationed In The Municipality Of Isulan And Tacurong City, Further Amending For The Purpose Section 14, Paragraph (M) Of Batas Pambansa Blg. 129, Otherwise Known As "The Judiciary Reorganization Act Of 1990," As Amended And Appropriating Funds Therefor',
            'serial_title': 'Republic Act No. 11455',
            'statute_date': '2019-08-30'
        },
        x x x  # these are the different statutes that affect the base statute bp 129
    ]
}
```
