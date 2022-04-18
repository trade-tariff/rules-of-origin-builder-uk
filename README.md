# Convert Word rules of origin documents to usable JSON format

## Implementation steps

- Create and activate a virtual environment, e.g.

  `python3 -m venv venv/`
  `source venv/bin/activate`

- Environment variable settings

  - n/a

- Install necessary Python modules via `pip3 install -r requirements.txt`

## Usage

### To translate a Word document:

The following are in a modern 2-column format
`python3 process.py "Canada PSR.docx"`
`python3 process.py "EU PSR.docx"`
`python3 process.py "Turkey PSR.docx"`
`python3 process.py "Japan PSR.docx"`

The remainder are in an old-style 3- or 4-column format, which requires significantly different processing
