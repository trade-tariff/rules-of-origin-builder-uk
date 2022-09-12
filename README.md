# Convert Word rules of origin documents to usable JSON format

Used for OTT strategic - UK data

## Implementation steps

- Create and activate a virtual environment, e.g.

  `python3 -m venv venv/`

  `source venv/bin/activate`

## Environment variable settings:

### Paths to lookups

- code_list=file where latest commodity coe list is stored
- all_rules_path=where the XI rule classes are stored
- ott_path=folder in which to copy files for OTT prototype preview

### Configurations
- modern_documents="EU,Japan,Turkey,Canada"
- validate_tables=[0|1]
- create_json=[0|1]
- validate_commodities=[0|1]
- validate_min_max=[0|1]

## Installation

- Install necessary Python modules via `pip3 install -r requirements.txt`

## Usage

### To translate a Word document:

The following are in a modern 2-column format
- `python3 process.py "EU PSR.docx"`
- `python3 process.py "Japan PSR.docx"`
- `python3 process.py "Turkey PSR.docx"`
- `python3 process.py "Canada PSR.docx"`
- `python3 process.py "Albania PSR.docx"`

The following are in an inherited 3- or 4 column format
- `python3 process.py "SACUM PSR.docx"`
- `python3 process.py "Ukraine PSR.docx"`
etc.


To batch process all documents (both new and legacy)
- `python3 batch.py`
