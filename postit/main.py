from postit.documents import generate_documents
from postit.processor import process

# Temporary test code

generate_documents(["/Users/bho/code/conquest-server/app/**/*.py"], "./data/documents")
process(
    ["./data/documents/*"],
    ["DocLengthChars", "ParagraphLengthChars", "NumDocs"],
    "test-exp",
)
