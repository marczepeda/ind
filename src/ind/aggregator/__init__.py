'''
src/ind/aggregator/
├── __init__.py                 Initializer
├── cli.py                      Command Line Interface (parser & run)
├── orchestrator.py             Data orchestration layer
├── utils.py                    Utilites
├── sources/
    ├── __init__.py
    ├── openfda.py              openfda module search + flatteners
    ├── uspto.py                # USPTO search + flatteners
    ├── clinicaltrials.py       # CT.gov search + flatteners
    ├── # later: sec.py, pubmed.py, etc.
├── render/
    ├── __init__.py
    ├── html.py                 HTML table rows and cards
    ├── csv.py                  CSV helper
'''