# Evaluation

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

```py
>>> from sqlpyd import Connection
>>> from corpus_x.__main__ import get_codification
>>> code_pk = "mv-2022-ra-386-modern-civil-code-v1"
>>> c = Connection(DatabasePath="x.db", WAL=True)
>>> code_detail = get_codification(c, code_pk)
{ 'created': 1673686439.0847127,
  'modified': 1673686439.0847127,
  'title': 'Modern Civil Code',
  'description': 'A Codification of Republic Act No. 386, As Amended.',
  'date': '2022-10-01',
  'statute_category': 'ra',
  'statute_serial_id': '386',
  'statute_id': 'ra-386-june-18-1949',
  'statute_date': '1949-06-18',
  'statute_titles': [{'title': 'New Civil Code', 'category': 'alias'},
    {'title': 'Civil Code of 1950', 'category': 'alias'},
    {'title': 'Civil Code of the Philippines', 'category': 'short'},
    {'title': 'Republic Act No. 386', 'category': 'serial'},
    {'title': 'An Act to Ordain and Institute the Civil Code of the Philippines',
    'category': 'official'}],
  'units': [{'item': 'Modern Civil Code',  # this is the nested tree that can be styled via html / css / js
    'id': '1.',
    'units': [{'item': 'Container 1',
      'caption': 'Preliminary Title',
      'id': '1.1.',
      'units': [{'item': 'Chapter 1',
        'caption': 'Effect and Application of Laws',
        'id': '1.1.1.',
        'units': [{'item': 'Article 1',
          'content': 'This Act shall be known as the "Civil Code of the Philippines." (n)',
          'id': '1.1.1.1.',
          'units': []},
        {'item': 'Article 2',
          'content': 'Laws shall take effect after fifteen days following the completion of their publication either in the Official Gazette or in a newspaper of general circulation in the Philippines, unless it is otherwise provided. (1a)',
          'id': '1.1.1.2.',
        }]}]}]}],
  'author_list': [{'id': 'mv', 'display': 'Marcelino Veloso III', 'img': 'members-mv'}],
  'event_statute_affectors': [{'id': 'ra-11057-august-17-2018',
    'serial_title': 'Republic Act No. 11057',
    'official_title': 'An Act Strengthening The Secured Transactions Legal Framework In The Philippines. Which Shall Provide For The Creation, Perfection, Determination Of Priority, Establishment Of A Centralized Notice Registry, And Enforcement Of Security Interests In Personal Property, And For Other Purposes',
    'statute_date': '2018-08-17'},
  {'id': 'ra-10172-august-15-2012',
    'serial_title': 'Republic Act No. 10172',
    'official_title': 'An Act Further Authorizing The City Or Municipal Civil Registrar Or The Consul General To Correct Clerical Or Typographical Errors In The Day And Month In The Date Of Birth Or Sex Of A Person Appearing In The Civil Register Without Need Of A Judicial Order, Amending For This Purpose Republic Act Numbered Ninety Forty-Eight',
    'statute_date': '2012-08-15'},
  ...]
}
```
