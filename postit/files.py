import gcsfs
import glob
import os
import shutil

from enum import Enum


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

    def read(self, path: str) -> str:
        """
        Read the contents of a local file and return it as a string.

        Args:
            path (str): The path to a local file.

        Returns:
            str: The contents of the file as a string.
        """
        with open(path, "rb") as file:
            return file.read().decode(errors="ignore")

    def write(self, path: str, content: str) -> None:
        """
        Write the given content to the specified local file path.

        Args:
            path (str): The path of the file to write.
            content (str): The content to write to the file.
        """
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path, exist_ok=True)

        with open(path, "w") as file:
            file.write(content)

    def remove(self, path: str) -> None:
        """
        Removes a local file or directory at the given path.

        Args:
            path (str): The path to the file or directory to be removed.
        """
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    def glob(self, path: str) -> list[str]:
        """
        Returns a list of local file paths that match the specified pattern.

        Args:
            path (str): The pattern to match against file paths.

        Returns:
            list[str]: A list of file paths that match the specified pattern.
        """
        return glob.glob(path, recursive=True)

    def is_file(self, path: str) -> bool:
        """
        Checks if the given path is a file.

        Args:
            path (str): The path to check.

        Returns:
            bool: True if the path is a file, False otherwise.
        """
        return os.path.isfile(path)

    @staticmethod
    def is_glob(path: str) -> bool:
        """
        Checks if the given path is a glob pattern.

        Args:
            path (str): The path to check.

        Returns:
            bool: True if the path is a glob pattern, False otherwise.
        """
        return any(char in path for char in ["*", "?", "[", "]"])


class GSFileClient(FileClient):
    """
    A file client implementation for Google Cloud Storage (GCS).
    """

    gcs = gcsfs.GCSFileSystem()

    def read(self, path: str) -> str:
        """
        Read the contents of a file from Google Cloud Storage.

        Args:
            path (str): The remote path of the file to read.

        Returns:
            str: The contents of the file as a string.
        """
        with self.gcs.open(path, "rb") as file:
            return file.read().decode(errors="ignore")

    def write(self, path: str, content: str) -> None:
        """
        Write content to a file in Google Cloud Storage.

        Args:
            path (str): The remote path of the file to write.
            content (str): The content to write to the file.
        """
        with self.gcs.open(path, "w") as file:
            file.write(content)

    def remove(self, path: str) -> None:
        """
        Remove a file or directory from Google Cloud Storage.

        Args:
            path (str): The remote path of the file or directory to remove.
        """
        self.gcs.rm(path, recursive=True)

    def glob(self, path: str) -> list[str]:
        """
        Glob for files in Google Cloud Storage.

        Args:
            path (str): The glob pattern to match.

        Returns:
            list[str]: A list of file paths matching the glob pattern.
        """
        paths = self.gcs.glob(path)
        return [f"gs://{path}" for path in paths]

    def is_file(self, path: str) -> bool:
        """
        Checks if the given path is a file in Google Cloud Storage.

        Args:
            path (str): The path to check.

        Returns:
            bool: True if the path is a file, False otherwise.
        """
        return self.gcs.isfile(path)


class S3FileClient(FileClient):
    """
    A file client for interacting with files stored in Amazon S3.

    TODO: Implement S3 file operations.
    """

    pass
