# Convert Word rules of origin documents to usable JSON format

Used for OTT strategic - UK data

## Implementation steps

- Create and activate a virtual environment, e.g.

  `python3 -m venv venv/`

  `source venv/bin/activate`

## Environment variable settings:

### Paths to lookups

- code_list=file where latest commodity code list is stored
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

- `python3 process.py "Albania PSR.docx"`
- `python3 process.py "Andean PSR.docx"`
- `python3 process.py "Cameroon PSR.docx"` -- does not work
- `python3 process.py "Canada PSR.docx"`
- `python3 process.py "Cariforum PSR.docx"`
- `python3 process.py "Central-America PSR.docx"`
- `python3 process.py "Chile PSR.docx"`
- `python3 process.py "CotedIvoire PSR.docx"`
- `python3 process.py "DCTS-General-Enhanced.docx"`
- `python3 process.py "DCTS-LDCS PSR.docx"`
- `python3 process.py "ESA PSR.docx"`
- `python3 process.py "EU PSR.docx"`
- `python3 process.py "Faroe-Islands PSR.docx"`
- `python3 process.py "Georgia PSR.docx"`
- `python3 process.py "Ghana PSR.docx"`
- `python3 process.py "GSP PSR.docx"`
- `python3 process.py "Iceland-Norway PSR.docx"`
- `python3 process.py "Israel PSR.docx"`
- `python3 process.py "Japan PSR.docx"`
- `python3 process.py "Jordan PSR.docx"` -- Done
- `python3 process.py "Kenya PSR.docx"`
- `python3 process.py "Kosovo PSR.docx"`
- `python3 process.py "Lebanon PSR.docx"`
- `python3 process.py "Mexico PSR.docx"`
- `python3 process.py "Moldova PSR.docx"`
- `python3 process.py "Morocco PSR.docx"`
- `python3 process.py "North-Macedonia PSR.docx"`
- `python3 process.py "OCT PSR.docx"`
- `python3 process.py "Pacific PSR.docx"`
- `python3 process.py "Palestinian-Authority PSR.docx"`
- `python3 process.py "SACUM PSR.docx"`
- `python3 process.py "Serbia PSR.docx"`
- `python3 process.py "Singapore PSR.docx"`
- `python3 process.py "South Korea PSR.docx"`
- `python3 process.py "Switzerland-Liechtenstein PSR.docx"`
- `python3 process.py "Tunisia PSR.docx"`
- `python3 process.py "Turkey PSR.docx"`
- `python3 process.py "Ukraine PSR.docx"`
- `python3 process.py "Vietnam PSR.docx"`


To batch process all documents (both new and legacy)
- `python3 batch.py`
