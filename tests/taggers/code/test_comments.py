import pytest

from postit.taggers.code.comments import CodeComments, CodeLicenses
from postit.tagging import TagResult
from postit.types import Doc
from unittest.mock import patch


@pytest.fixture
def code_comments():
    return CodeComments()


@pytest.fixture
def code_licenses():
    return CodeLicenses()


#####################
# CodeComments tests
#####################


def test_single_line_comments(code_comments):
    content = """
    # This is a single line comment
    print("Hello, World!") // Another comment
    """
    doc = Doc(id=0, source="test.py", content=content)
    result = code_comments.tag(doc)

    assert isinstance(result, TagResult)
    assert len(result.tags) == 2

    assert result.tags[0].name == "comments"
    assert result.tags[1].name == "comments"

    assert (
        doc.content[result.tags[0].start : result.tags[0].end]
        == "# This is a single line comment"
    )
    assert (
        doc.content[result.tags[1].start : result.tags[1].end] == "// Another comment"
    )


def test_multi_line_comments(code_comments):
    content = """
    /* This is a 
    multi-line comment */
    var x = 10;
    <!-- HTML comment -->
    """
    doc = Doc(id=0, source="test.py", content=content)
    result = code_comments.tag(doc)

    assert isinstance(result, TagResult)
    assert len(result.tags) == 2

    assert result.tags[0].name == "comments"
    assert result.tags[1].name == "comments"

    assert (
        doc.content[result.tags[0].start : result.tags[0].end]
        == "/* This is a \n    multi-line comment */"
    )
    assert (
        doc.content[result.tags[1].start : result.tags[1].end]
        == "<!-- HTML comment -->"
    )


def test_block_comments(code_comments):
    content = """
// This is the first line of a block comment
// This is the second line of a block comment
    
var x = 10;
# This is a single line comment
    """
    doc = Doc(id=0, source="test.py", content=content)
    result = code_comments.tag(doc)

    assert isinstance(result, TagResult)
    assert len(result.tags) == 2

    assert result.tags[0].name == "comments"
    assert result.tags[1].name == "comments"

    assert (
        doc.content[result.tags[0].start : result.tags[0].end]
        == "// This is the first line of a block comment\n// This is the second line of a block comment"
    )
    assert (
        doc.content[result.tags[1].start : result.tags[1].end]
        == "# This is a single line comment"
    )


def test_no_comments(code_comments):
    content = """
    print("This is a string with # symbols inside")
    var y = 'Another string with // symbols';
    """
    doc = Doc(id=0, source="test.py", content=content)
    result = code_comments.tag(doc)

    assert isinstance(result, TagResult)
    assert len(result.tags) == 0


def test_mixed_content(code_comments):
    content = """
    // Single line comment
    var z = 42; /* Inline multi-line comment */ var a = 1;
    """
    doc = Doc(id=0, source="test.py", content=content)
    result = code_comments.tag(doc)

    assert isinstance(result, TagResult)
    assert len(result.tags) == 2

    assert result.tags[0].name == "comments"
    assert result.tags[1].name == "comments"

    # Check that the comments are correctly identified
    assert (
        doc.content[result.tags[0].start : result.tags[0].end]
        == "// Single line comment"
    )
    assert (
        doc.content[result.tags[1].start : result.tags[1].end]
        == "/* Inline multi-line comment */"
    )


######################
# CodeLicenses tests
######################


@patch.object(CodeLicenses, "imports", new_callable=dict)
def test_license_in_comments(mock_imports, code_licenses):
    content = """
// Just a regular comment
/* Copyright 2024 Brennen. All rights reserved. */
    """
    doc = Doc(id=1, source="test_license.py", content=content)

    # Mock the result of code_comments
    mock_imports["code_comments/comments"] = {doc.id: [[0, 25, 1], [26, 77, 1]]}

    result = code_licenses.tag(doc)

    assert isinstance(result, TagResult)
    assert len(result.tags) == 1

    assert result.tags[0].name == "notice"

    # Check the content of the tagged license comment
    assert (
        doc.content[result.tags[0].start : result.tags[0].end].strip()
        == "/* Copyright 2024 Brennen. All rights reserved. */"
    )


@patch.object(CodeLicenses, "imports", new_callable=dict)
def test_no_license_comments(mock_imports, code_licenses):
    content = """
    # Just a regular comment
    // Another comment without legal terms
    """
    doc = Doc(id=2, source="test_no_license.py", content=content)

    # Mock the result of code_comments
    mock_imports["code_comments/comments"] = {
        doc.id: [(0, 24, 1), (25, 61, 1)]  # Indexes of the comments
    }

    result = code_licenses.tag(doc)

    assert isinstance(result, TagResult)
    assert len(result.tags) == 0


@patch.object(CodeLicenses, "imports", new_callable=dict)
def test_mixed_license_comments(mock_imports, code_licenses):
    content = """
// General comment
/* This software is licensed under the MIT License. */
var x = 10;
// Copyright 2024 Brennen
    """
    doc = Doc(id=3, source="test_mixed_license.py", content=content)

    # Mock the result of code_comments
    mock_imports["code_comments/comments"] = {
        doc.id: [[0, 18, 1], [19, 74, 1], [86, 112, 1]]  # Indexes of the comments
    }

    result = code_licenses.tag(doc)

    assert isinstance(result, TagResult)
    assert len(result.tags) == 2

    assert result.tags[0].name == "notice"
    assert result.tags[1].name == "notice"

    # Check the content of the tagged license comments
    assert (
        doc.content[result.tags[0].start : result.tags[0].end].strip()
        == "/* This software is licensed under the MIT License. */"
    )
    assert (
        doc.content[result.tags[1].start : result.tags[1].end].strip()
        == "// Copyright 2024 Brennen"
    )
