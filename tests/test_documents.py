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
    mock_file_client_root = MagicMock()
    mock_file_client_subfolder = MagicMock()
    mock_file_client_output = MagicMock()

    def get_mock_for_target(target):
        if target == "root":
            return mock_file_client_root
        elif target == "subfolder":
            return mock_file_client_subfolder
        elif target == "output":
            return mock_file_client_output
        return None

    # Set the side_effect to use the function above
    mock_file_client_cls.get_for_target.side_effect = get_mock_for_target

    mock_file_client_root.glob.return_value = ["subfolder"]
    mock_file_client_subfolder.glob.return_value = ["file1", "file2"]
    mock_file_client_subfolder.read.side_effect = ["content1", "content2"]
    mock_file_client_subfolder.get_file_count.return_value = 2

    DocumentGenerator.generate(["root"], "output", keep_raw=False)

    mock_file_client_cls.get_for_target.assert_any_call("root")
    mock_file_client_cls.get_for_target.assert_any_call("output")

    expected_output = (
        '{"id": 0, "source": "file1", "content": "content1"}\n'
        '{"id": 1, "source": "file2", "content": "content2"}\n'
    )
    mock_file_client_output.write.assert_called_with(
        "output/subfolder.jsonl", expected_output
    )
    mock_file_client_subfolder.remove.assert_called_with("subfolder")
