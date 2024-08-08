import pytest

from postit.documents import DocumentGenerator, get_top_folder
from unittest.mock import MagicMock, patch


@pytest.mark.parametrize(
    "input_path, expected_top_folder",
    [
        ("root/subfolder/*", "root/subfolder"),
        ("root/subfolder/?*.gz", "root/subfolder"),
        ("root/**", "root"),
        ("root/**/[a-z].gz", "root"),
        ("root/**/subfolder", "root/subfolder"),
        ("root/**/subfolder/*", "root/subfolder"),
        ("root/**/subfolder/?*.gz", "root/subfolder"),
        ("root/**/subfolder/**", "root/subfolder"),
        ("root/**/subfolder/**/[a-z].gz", "root/subfolder"),
    ],
)
def test_get_top_folder(input_path, expected_top_folder):
    assert get_top_folder(input_path) == expected_top_folder


@patch("postit.documents.FileClient")
def test_documents_generator(mock_file_client_cls):
    mock_file_client = MagicMock()
    mock_file_client_cls.get_for_target.return_value = mock_file_client

    mock_file_client.glob.return_value = ["file1", "file2"]
    mock_file_client.read.side_effect = ["content1", "content2"]
    mock_file_client.get_file_count.return_value = 2

    DocumentGenerator.generate(["root"], "output", keep_raw=False)

    mock_file_client_cls.get_for_target.assert_any_call("root")
    mock_file_client_cls.get_for_target.assert_any_call("output")

    expected_output = (
        '{"id": 0, "source": "file1", "content": "content1"}\n'
        '{"id": 1, "source": "file2", "content": "content2"}\n'
    )
    mock_file_client.write.assert_called_with("output/root.jsonl", expected_output)
    mock_file_client.remove.assert_called_with("root")
