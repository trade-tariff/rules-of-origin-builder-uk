from classes.roo_document import RooDocument
import classes.globals as g


list = [
    "Albania PSR.docx",
    "Andean PSR.docx",
    "Cameroon PSR.docx",
    "Canada PSR.docx",
    "Cariforum PSR.docx",
    "Central-America PSR.docx",
    "Chile PSR.docx",
    "Egypt PSR.docx",
    "ESA PSR.docx",
    "EU PSR.docx",
    "Faroe-Islands PSR.docx",
    "Georgia PSR.docx",
    "Ghana PSR.docx",
    "Iceland-Norway PSR.docx",
    "Israel PSR.docx",
    "Japan PSR.docx",
    "Jordan PSR.docx",
    "Kosovo PSR.docx",
    "Lebanon PSR.docx",
    "Mexico PSR.docx",
    "Moldova PSR.docx",
    "Morocco PSR.docx",
    "North-Macedonia PSR.docx",
    "Pacific PSR.docx",
    "Palestinian-Authority PSR.docx",
    "SACUM PSR.docx",
    "Serbia PSR.docx",
    "Singapore PSR.docx",
    "South Korea PSR.docx",
    "Switzerland-Liechtenstein PSR.docx",
    "Tunisia PSR.docx",
    "Turkey PSR.docx",
    "Ukraine PSR.docx",
    "Vietnam PSR.docx"
]

g.clear()
for item in list:
    if item[0] != "":
        document = RooDocument(item)
