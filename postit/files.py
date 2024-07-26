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
    @staticmethod
    def get_for_target(path: str) -> "FileClient":
        if path.startswith(FileClientTarget.GS.value):
            return GSFileClient()
        elif path.startswith(FileClientTarget.S3.value):
            return S3FileClient()
        else:
            return FileClient()

    def read(self, path: str) -> str:
        with open(path, "rb") as file:
            return file.read().decode(errors="ignore")

    def write(self, path: str, content: str) -> None:
        dir_path = os.path.dirname(path)
        os.makedirs(dir_path, exist_ok=True)

        with open(path, "w") as file:
            file.write(content)

    def remove(self, path: str) -> None:
        print(path)
        if os.path.isdir(path):
            shutil.rmtree(path)
        else:
            os.remove(path)

    def glob(self, path: str) -> list[str]:
        return glob.glob(path, recursive=True)


class GSFileClient(FileClient):
    gcs = gcsfs.GCSFileSystem()

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


class S3FileClient(FileClient):
    pass
