from postit.files import FileClient, GSFileClient, S3FileClient
from unittest import mock


def test_get_for_target():
    assert isinstance(FileClient.get_for_target("gs://bucket/file"), GSFileClient)
    assert isinstance(FileClient.get_for_target("s3://bucket/file"), S3FileClient)
    local_client = FileClient.get_for_target("local/file")
    assert isinstance(local_client, FileClient)
    assert not isinstance(local_client, GSFileClient)
    assert not isinstance(local_client, S3FileClient)


@mock.patch("builtins.open", new_callable=mock.mock_open, read_data=b"file content")
def test_local_read(mock_open):
    client = FileClient()
    result = client.read("/local/path")
    mock_open.assert_called_once_with("/local/path", "rb")
    assert result == "file content"


@mock.patch("builtins.open", new_callable=mock.mock_open)
@mock.patch("os.makedirs")
def test_local_write(mock_makedirs, mock_open):
    client = FileClient()
    client.write("/local/path", "file content")
    mock_makedirs.assert_called_once_with("/local", exist_ok=True)
    mock_open.assert_called_once_with("/local/path", "w")
    mock_open().write.assert_called_once_with("file content")


@mock.patch("os.remove")
def test_local_remove_file(mock_remove):
    client = FileClient()
    client.remove("/local/file")
    mock_remove.assert_called_once_with("/local/file")


@mock.patch("os.path.isdir", return_value=True)
@mock.patch("shutil.rmtree")
def test_local_remove_directory(mock_rmtree, mock_isdir):
    client = FileClient()
    client.remove("/local/directory")
    mock_isdir.assert_called_once_with("/local/directory")
    mock_rmtree.assert_called_once_with("/local/directory")


@mock.patch("glob.glob", return_value=["/local/file1", "/local/file2"])
def test_local_glob(mock_glob):
    client = FileClient()
    result = client.glob("/local/*")
    mock_glob.assert_called_once_with("/local/*", recursive=True)
    assert result == ["/local/file1", "/local/file2"]


@mock.patch(
    "gcsfs.GCSFileSystem.open",
    new_callable=mock.mock_open,
    read_data=b"gs file content",
)
def test_gs_read(mock_open):
    client = GSFileClient()
    result = client.read("gs://bucket/file")
    mock_open.assert_called_once_with("gs://bucket/file", "rb")
    assert result == "gs file content"


@mock.patch("gcsfs.GCSFileSystem.open", new_callable=mock.mock_open)
def test_gs_write(mock_open):
    client = GSFileClient()
    client.write("gs://bucket/file", "gs file content")
    mock_open.assert_called_once_with("gs://bucket/file", "w")
    mock_open().write.assert_called_once_with("gs file content")


@mock.patch("gcsfs.GCSFileSystem.rm")
def test_gs_remove(mock_rm):
    client = GSFileClient()
    client.remove("gs://bucket/file")
    mock_rm.assert_called_once_with("gs://bucket/file", recursive=True)


@mock.patch.object(GSFileClient, "gcs")
def test_glob_gs(mock_gcs):
    mock_gcs.glob.return_value = ["bucket/file1", "bucket/file2"]
    client = GSFileClient()
    result = client.glob("gs://bucket/*")
    mock_gcs.glob.assert_called_once_with("gs://bucket/*")
    assert result == ["gs://bucket/file1", "gs://bucket/file2"]
