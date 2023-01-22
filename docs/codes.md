# Codifications

## Codification path/s

All codifications are sourced from a parent `/codifications`

Each child folder of the parent is a category /codifications/`ra`, /codifications/`roc`, etc

Each child folder of a category is the *serial id* of such category, e.g. /codifications/ra/`386`

Each file in the latter folder is named after its identifier, e.g. `mv-civil-v1.yaml`

## Codification creation and population

It takes about **~3 minutes** to populate all the codification tables.

```py
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
