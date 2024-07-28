import pytest

from postit.registry import TaggerRegistry
from postit.taggers.length import (
    DocLengthChars,
    NumDocs,
    ParagraphLengthChars,
)
from postit.tagging import DocTagger, FileTagger, TagResult
from postit.types import Doc, File, FloatTag


def test_doc_length_chars():
    doc = Doc(idx=0, source="/test/path.py", content="This is a test document.")
    tagger = TaggerRegistry.get("DocLengthChars")()
    result = tagger.tag(doc)

    assert isinstance(result, TagResult)
    assert len(result.tags) == 1
    assert isinstance(result.tags[0], FloatTag)
    assert result.tags[0].value == len(doc.content)


def test_paragraph_length_chars():
    doc_content = "Paragraph one.\nParagraph two.\nParagraph three."
    doc = Doc(idx=0, source="/test/path.py", content=doc_content)
    tagger = TaggerRegistry.get("ParagraphLengthChars")()
    result = tagger.tag(doc)

    paragraphs = doc_content.split("\n")
    assert isinstance(result, TagResult)
    assert len(result.tags) == len(paragraphs)

    for i, paragraph in enumerate(paragraphs):
        assert isinstance(result.tags[i], FloatTag)
        assert result.tags[i].value == len(paragraph)


def test_num_docs():
    file_content = "Doc1\nDoc2\nDoc3"
    file = File(source="/test/path.py", content=file_content)
    tagger = TaggerRegistry.get("NumDocs")()
    result = tagger.tag(file)

    assert isinstance(result, TagResult)
    assert len(result.tags) == 1
    assert isinstance(result.tags[0], FloatTag)
    assert result.tags[0].value == len(file.content)
