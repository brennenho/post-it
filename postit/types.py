import json

from abc import ABC, abstractmethod
from typing import Union


class Source(ABC):
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
    __slots__ = "id", "content"

    def __init__(self, id: int, source: str, content: str):
        super().__init__(source)
        self.id = id
        self.content = content

    def get_tags(self) -> str:
        return json.dumps(
            {
                "id": self.id,
                "source": self.source,
                "tags": self.tags,
            }
        )


class File(Source):
    __slots__ = "content"

    def __init__(self, source: str, content: list[Doc]):
        super().__init__(source)
        self.content = content

    def get_tags(self) -> str:
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

        content = [
            Doc(data["id"], data["source"], data["content"])
            for line in raw.strip().splitlines()
            for data in [json.loads(line)]
        ]
        return File(path, content)


class Tag(ABC):
    """
    Abstract base class for tags.
    NOTE: Do not instantiate this class directly. Use FloatTag or StrTag instead.

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
        pass


class FloatTag(Tag):
    """
    Tags a floating-point value.
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
    Tags a string value.
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
    Results of a tagging operation.
    """

    __slots__ = "source", "tags"

    def __init__(self, source: Source, tags: list[Tag]):
        self.source = source
        self.tags = tags
