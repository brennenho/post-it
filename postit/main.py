from postit.documents import generate_documents
from postit.mixer import Condition, Mixer, MixerConfig
from postit.processor import process

# Temporary test code

generate_documents(["/Users/bho/code/conquest-server/app/**/*.py"], "./data/documents")
process(
    ["./data/documents/*"],
    ["DocLengthChars", "ParagraphLengthChars"],
    "length",
)
process(
    ["./data/documents/*"],
    ["NumDocs"],
    "num-docs",
)
mixer_config = MixerConfig(
    name="test-mix",
    tags=["length", "num-docs"],
    input_paths=["./data/documents/*"],
    conditions={
        "include": [
            Condition(tag="ParagraphLengthChars", operator=">", value=0),
        ],
        "exclude": [Condition(tag="ParagraphLengthChars", operator=">", value=30)],
    },
)

mixer = Mixer(mixer_config)
mixer.mix()
