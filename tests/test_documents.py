from postit.documents import generate_documents, get_top_folder
from unittest.mock import patch

def test_get_top_folder():
    assert get_top_folder("root/*") == "root"
    assert get_top_folder("root/subfolder/*") == "root/subfolder"
    assert get_top_folder("root/subfolder/?*.gz") == "root/subfolder"
    assert get_top_folder("root/**") == "root"
    assert get_top_folder("root/**/[a-z].gz") == "root"
    assert get_top_folder("root/**/subfolder") == "root/subfolder"
    assert get_top_folder("root/**/subfolder/*") == "root/subfolder"
    assert get_top_folder("root/**/subfolder/?*.gz") == "root/subfolder"
    assert get_top_folder("root/**/subfolder/**") == "root/subfolder"
    assert get_top_folder("root/**/subfolder/**/[a-z].gz") == "root/subfolder"

@patch("postit.documents.FileClient")
def test_generate_documents(mock_file_client):
    mock_file_client.get_for_target.return_value.glob.return_value = ["file1", "file2"]
    mock_file_client.get_for_target.return_value.read.side_effect = ["content1", "content2"]

    generate_documents(["root"], "output", keep_raw=False)

    mock_file_client.get_for_target.assert_called_with("output")
    mock_file_client.get_for_target.return_value.write.assert_called_with("output/root.jsonl", '{"idx": 0, "source": "file1", "content": "content1"}\n{"idx": 1, "source": "file2", "content": "content2"}\n')
    mock_file_client.get_for_target.return_value.remove.assert_called_with("root")