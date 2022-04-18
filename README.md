# Download and parse files from the CDS download service

## Implementation steps

- Create and activate a virtual environment, e.g.

  `python3 -m venv venv/`
  `source venv/bin/activate`

- Environment variable settings

  - domain=root domain from which to download GZIP files
  - client_secret
  - client_id
  - DATABASE_UK=postgres connection string
  - IMPORT_FOLDER=folder to which to copy files, for import
  - OVERWRITE_XLSX=0|1 - 0 will run parser on all files; 1 will only parse files that are missing

- Install necessary Python modules via `pip3 install -r requirements.txt`

## Usage

### To download CDS extract files:
`python3 download.py`

### To parse CDS extract files into Excel:
`python3 parse.py`

### To go to the Excel folder:
`python3 dest.py`

### To run all three of the steps above:
`python3 parse.py`

