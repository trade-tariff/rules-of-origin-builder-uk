from classes.roo_document import RooDocument
import classes.globals as g


list = [
    "xAlbania PSR.docx",
    "xAndean PSR.docx",
    "xCameroon PSR.docx",
    "xCanada PSR.docx",
    "xCariforum PSR.docx",
    "xCentral-America PSR.docx",
    "xChile PSR.docx",
    "xEgypt PSR.docx",
    "xESA PSR.docx",
    "xEU PSR.docx",
    "xFaroe-Islands PSR.docx",
    "xGeorgia PSR.docx",
    "xGhana PSR.docx",
    "xIceland-Norway PSR.docx",
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
    if item[0] != "x":
        document = RooDocument(item)
