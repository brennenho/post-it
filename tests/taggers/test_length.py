from postit.registry import TaggerRegistry
from postit.tagging import TagResult
from postit.types import Doc, File, FloatTag


def test_doc_length():
    doc_content = "This is a test document. It has several words."
    doc = Doc(idx=0, source="/test/path.py", content=doc_content)
    tagger = TaggerRegistry.get("DocLength")()
    result = tagger.tag(doc)

    assert isinstance(result, TagResult)
    assert len(result.tags) == 2

    char_tag = result.tags[0]
    word_tag = result.tags[1]

    assert isinstance(char_tag, FloatTag)
    assert char_tag.name == "chars"
    assert char_tag.value == len(doc_content)
    assert char_tag.start == 0
    assert char_tag.end == len(doc_content)

    assert isinstance(word_tag, FloatTag)
    assert word_tag.name == "words"
    assert word_tag.value == len(doc_content.split())
    assert word_tag.start == 0
    assert word_tag.end == len(doc_content)


def test_paragraph_length():
    doc_content = "Paragraph one.\nParagraph two.\nParagraph three."
    doc = Doc(idx=0, source="/test/path.py", content=doc_content)
    tagger = TaggerRegistry.get("ParagraphLength")()
    result = tagger.tag(doc)

    paragraphs = doc_content.split("\n")
    assert isinstance(result, TagResult)
    assert len(result.tags) == (len(paragraphs) * 2)

    for i, paragraph in enumerate(paragraphs):
        char_tag = result.tags[i * 2]
        word_tag = result.tags[i * 2 + 1]

        assert isinstance(char_tag, FloatTag)
        assert char_tag.name == "chars"
        assert char_tag.value == len(paragraph)
        assert char_tag.start == sum(
            len(p) + 1 for p in paragraphs[:i]
        )  # previous paragraphs plus newlines
        assert char_tag.end == char_tag.start + len(paragraph)

        assert isinstance(word_tag, FloatTag)
        assert word_tag.name == "words"
        assert word_tag.value == len(paragraph.split())
        assert word_tag.start == char_tag.start
        assert word_tag.end == char_tag.end


def test_num_docs():
    file_content = "Doc1\nDoc2\nDoc3"
    file = File(source="/test/path.py", content=file_content)
    tagger = TaggerRegistry.get("NumDocs")()
    result = tagger.tag(file)

    assert isinstance(result, TagResult)
    assert len(result.tags) == 1
    assert isinstance(result.tags[0], FloatTag)
    assert result.tags[0].value == len(file.content)
