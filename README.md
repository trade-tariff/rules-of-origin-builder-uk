# Convert Word rules of origin documents to usable JSON format

Used for OTT strategic - UK data

## Implementation steps

- Create and activate a virtual environment, e.g.

  `python -m venv venv/`

  `source venv/bin/activate`

## Environment variable settings:

### Paths to lookups

- code_list=file where latest commodity code list is stored
- all_rules_path=where the XI rule classes are stored
- ott_prototype_path=folder in which to copy files for OTT prototype preview

### Configurations
- modern_documents="EU,Japan,Turkey,Canada"
- validate_tables=[0|1]
- create_json=[0|1]
- check_coverage=[0|1]
- validate_min_max=[0|1]

## Installation

- Install necessary Python modules via `pip install -r requirements.txt`

## Usage

### To translate a Word document:

The following are in a modern 2-column format

- `python process.py "Canada PSR.docx"`
- `python process.py "EU PSR.docx"`
- `python process.py "Japan PSR.docx"`
- `python process.py "Turkey PSR.docx"`

And these are in the older but more common format

- `python process.py "Albania PSR.docx"`
- `python process.py "Andean PSR.docx"`
- `python process.py "Cameroon PSR.docx"`
- `python process.py "Cariforum PSR.docx"`
- `python process.py "Central-America PSR.docx"`
- `python process.py "Chile PSR.docx"`
- `python process.py "CotedIvoire PSR.docx"`
- `python process.py "DCTS-General-Enhanced PSR.docx"`
- `python process.py "DCTS-LDCS PSR.docx"`
- `python process.py "ESA PSR.docx"`
- `python process.py "Faroe-Islands PSR.docx"`
- `python process.py "Georgia PSR.docx"`
- `python process.py "Ghana PSR.docx"`
- `python process.py "GSP PSR.docx"` -- No longer needed
- `python process.py "Iceland-Norway PSR.docx"`
- `python process.py "Israel PSR.docx"`
- `python process.py "Jordan PSR.docx"`
- `python process.py "Kenya PSR.docx"`
- `python process.py "Kosovo PSR.docx"`
- `python process.py "Lebanon PSR.docx"`
- `python process.py "Mexico PSR.docx"`
- `python process.py "Moldova PSR.docx"`
- `python process.py "Morocco PSR.docx"`
- `python process.py "North-Macedonia PSR.docx"`
- `python process.py "OCT PSR.docx"`
- `python process.py "Pacific PSR.docx"`
- `python process.py "Palestinian-Authority PSR.docx"`
- `python process.py "SACUM PSR.docx"`
- `python process.py "Serbia PSR.docx"`
- `python process.py "Singapore PSR.docx"`
- `python process.py "South Korea PSR.docx"`
- `python process.py "Switzerland-Liechtenstein PSR.docx"`
- `python process.py "Tunisia PSR.docx"`
- `python process.py "Ukraine PSR.docx"`
- `python process.py "Vietnam PSR.docx"`
- `python process.py "Non-Preferential PSR.docx"`


To batch process all documents (both new and legacy)
- `python batch.py`


python process.py "Iceland-Norway PSR - step 3.docx"
