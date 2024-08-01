import json

from postit.types import Doc, File, FloatTag, StrTag, TagResult


def test_doc_initialization():
    doc = Doc(1, "source1", "content1")
    assert doc.idx == 1
    assert doc.source == "source1"
    assert doc.content == "content1"
    assert doc.tags == {}


def test_doc_get_tags():
    doc = Doc(1, "source1", "content1")
    expected_tags = json.dumps({"idx": 1, "source": "source1", "tags": {}})
    assert doc.get_tags() == expected_tags


def test_file_initialization():
    doc1 = Doc(1, "source1", "content1")
    doc2 = Doc(2, "source2", "content2")
    file = File("source_file", [doc1, doc2])
    assert file.source == "source_file"
    assert file.content == [doc1, doc2]
    assert file.tags == {}


def test_file_get_tags():
    doc1 = Doc(1, "source1", "content1")
    doc2 = Doc(2, "source2", "content2")
    file = File("source_file", [doc1, doc2])
    expected_tags = (
        json.dumps({"source": "source_file", "tags": {}})
        + "\n"
        + doc1.get_tags()
        + "\n"
        + doc2.get_tags()
    )

    assert file.get_tags() == expected_tags


def test_file_from_raw():
    raw_data = (
        json.dumps({"idx": 1, "source": "source1", "content": "content1"})
        + "\n"
        + json.dumps({"idx": 2, "source": "source2", "content": "content2"})
    )
    file = File.from_raw("source_file", raw_data)
    assert file.source == "source_file"
    assert len(file.content) == 2
    assert file.content[0].idx == 1
    assert file.content[0].source == "source1"
    assert file.content[0].content == "content1"
    assert file.content[1].idx == 2
    assert file.content[1].source == "source2"
    assert file.content[1].content == "content2"


def test_float_tag():
    tag = FloatTag("name", 0, 10, 0.5)
    assert tag.name == "name"
    assert tag.start == 0
    assert tag.end == 10
    assert tag.value == 0.5

    tag.value = 1.5
    assert tag.value == 1.5


def test_str_tag():
    tag = StrTag("name", 0, 10, "test")
    assert tag.name == "name"
    assert tag.start == 0
    assert tag.end == 10
    assert tag.value == "test"

    tag.value = "new_test"
    assert tag.value == "new_test"


def test_tag_result():
    doc = Doc(1, "source1", "content1")
    tag1 = FloatTag("tag1", 0, 10, 0.5)
    tag2 = StrTag("tag2", 11, 20, "test")
    tag_result = TagResult(doc, [tag1, tag2])
    assert tag_result.source == doc
    assert tag_result.tags == [tag1, tag2]
