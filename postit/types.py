import json

from abc import ABC, abstractmethod
from typing import Union


class Source(ABC):
    """
    Abstract base class for source objects.
    """

    __slots__ = "source", "tags"

    def __init__(self, source: str):
        self.source = source
        self.tags: dict[str, list] = {}

    def get_tags(self) -> str:
        """
        Gets the tags associated with the source.

        Returns:
            str: The tags associated with the source.
        """
        raise NotImplementedError


class Doc(Source):
    """
    Represents a document.

    Attributes:
        idx (int): The index of the document.
        content (str): The content of the document.
    """

    __slots__ = "idx", "content"

    def __init__(self, idx: int, source: str, content: str):
        super().__init__(source)
        self.idx = idx
        self.content = content

    def get_tags(self) -> str:
        """
        Get the tags of the document.

        Returns:
            str: A JSON string representing the document's tags.
        """
        return json.dumps(
            {
                "idx": self.idx,
                "source": self.source,
                "tags": self.tags,
            }
        )


class File(Source):
    """
    Represents a file containing a list of documents.

    Attributes:
        content (list[Doc]): The list of documents in the file.
    """

    __slots__ = "content"

    def __init__(self, source: str, content: list[Doc]):
        super().__init__(source)
        self.content = content

    def get_tags(self) -> str:
        """
        Returns the tags of the file and its documents.

        Returns:
            str: The JSONL string representation of the file's tags and the tags of its documents.
        """
        json_str = json.dumps(
            {
                "source": self.source,
                "tags": self.tags,
            }
        )
        return json_str + "\n" + "\n".join(doc.get_tags() for doc in self.content)

    @staticmethod
    def from_raw(path: str, raw: str) -> "File":
        """
        Creates a File object from raw data.

        Args:
            path (str): The path of the file.
            raw (str): The raw data representing the file.

        Returns:
            File: The created File object.
        """
        content = []
        for line in raw.strip().splitlines():
            data = json.loads(line)
            content.append(Doc(data["idx"], data["source"], data["content"]))
        return File(path, content)


class Tag(ABC):
    """
    Abstract base class for tags.

    Attributes:
        name (str): The name of the tag.
        start (int): The starting position of the tag.
        end (int): The ending position of the tag
    """

    __slots__ = "name", "start", "end"

    def __init__(self, name: str, start: int, end: int):
        self.name = name
        self.start = start
        self.end = end

    @property
    @abstractmethod
    def value(self) -> Union[float, str]:
        """
        Returns the value of the object.

        Returns:
            Union[float, str]: The value of the object, which can be either a float or a string.
        """
        pass


class FloatTag(Tag):
    """
    Represents a tag with a floating-point value.

    Attributes:
        value (float): The floating-point value associated with the tag.
    """

    __slots__ = "_value"

    def __init__(self, name: str, start: int, end: int, value: float):
        super().__init__(name, start, end)
        self._value = value

    @property
    def value(self) -> float:
        # Values are rounded to 4 decimal places
        return round(self._value, 4)

    @value.setter
    def value(self, value: float):
        self._value = value


class StrTag(Tag):
    """
    Represents a string tag.

    Attributes:
        value (str): The value of the tag.
    """

    __slots__ = "_value"

    def __init__(self, name: str, start: int, end: int, value: str):
        super().__init__(name, start, end)
        self.value = value

    @property
    def value(self) -> str:
        return self._value

    @value.setter
    def value(self, value: str):
        self._value = value


class TagResult(ABC):
    """
    Represents the result of a tagging operation.

    Attributes:
        source (Source): The source of the tagging operation.
        tags (list[Tag]): The list of tags associated with the source.
    """

    __slots__ = "source", "tags"

    def __init__(self, source: Source, tags: list[Tag]):
        self.source = source
        self.tags = tags
