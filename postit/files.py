import gcsfs
import glob
import os
import shutil

from enum import Enum
from typing import IO


class FileClientTarget(Enum):
    LOCAL = "local"
    GS = "gs://"
    S3 = "s3://"


class FileClient:
    """
    A base class for file clients. Supports local file operations.
    Derived classes add support for cloud storage services.
    """

    @staticmethod
    def get_for_target(path: str) -> "FileClient":
        """
        Returns a FileClient object based on the given local or remote path.

        Args:
            path (str): The path to a file or directory in local or remote storage.

        Returns:
            FileClient: An instance of the appropriate FileClient subclass based on the path.
        """
        if path.startswith(FileClientTarget.GS.value):
            return GSFileClient()
        elif path.startswith(FileClientTarget.S3.value):
            return S3FileClient()
        else:
            return FileClient()

    def open(self, path: str, mode: str) -> IO:
        return open(path, mode)

    def read(self, path: str) -> str:
        with open(path, "rb") as file:
            return file.read().decode(errors="ignore")

    def write(self, path: str, content: str) -> None:
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path, exist_ok=True)

        with open(path, "w") as file:
            file.write(content)

    def remove(self, path: str) -> None:
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    def glob(self, path: str) -> list[str]:
        return glob.glob(path, recursive=True)

    def is_file(self, path: str) -> bool:
        return os.path.isfile(path)

    def get_file_count(self, path: str) -> int:
        paths = self.glob(path)
        return sum([1 for p in paths if self.is_file(p)])

    @staticmethod
    def is_glob(path: str) -> bool:
        return any(char in path for char in ["*", "?", "[", "]"])


class GSFileClient(FileClient):
    """
    A file client implementation for Google Cloud Storage (GCS).
    """

    def __init__(self):
        self.gcs = gcsfs.GCSFileSystem()

    def open(self, path: str, mode: str) -> IO:
        return self.gcs.open(path, mode)

    def read(self, path: str) -> str:
        with self.gcs.open(path, "rb") as file:
            return file.read().decode(errors="ignore")

    def write(self, path: str, content: str) -> None:
        with self.gcs.open(path, "w") as file:
            file.write(content)

    def remove(self, path: str) -> None:
        self.gcs.rm(path, recursive=True)

    def glob(self, path: str) -> list[str]:
        paths = self.gcs.glob(path)
        return [f"gs://{path}" for path in paths]

    def is_file(self, path: str) -> bool:
        return self.gcs.isfile(path)

    def get_file_count(self, path: str) -> int:
        paths = self.glob(path)
        return sum([1 for p in paths if self.is_file(p)])


class S3FileClient(FileClient):
    """
    A file client for interacting with files stored in Amazon S3.

    TODO: Implement S3 file operations.
    """

    pass
