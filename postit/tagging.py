import json

from abc import ABC, abstractmethod
from collections import defaultdict
from postit.types import Doc, File, Source, TagResult
from typing import Any, Generic, TypeVar

T = TypeVar("T", bound=Source)


class BaseTagger(ABC, Generic[T]):
    """
    Base class for taggers.

    This class defines the common interface and behavior for taggers.
    NOTE: Do not inherit from this class directly. Inherit from DocTagger or FileTagger instead.

    Attributes:
        name (str): The name of the tagger.
        dependencies (list[str]): The list of tagger dependencies.
        imports (dict[str, dict]): The imported tags from other experiments.
            NOTE: This is generated automatically by the processor. You should not need to modify this.
    """

    name: str
    dependencies: list[str] = []
    imports: dict[str, dict] = {}

    @abstractmethod
    def tag(self, source: T, **kwargs: Any) -> TagResult:
        """
        Tags the given source object and returns the result.
        This method should be overridden by custom taggers.

        Args:
            source (T): The source object to be tagged. (Doc or File)

        Returns:
            TagResult: The result of the tagging operation.
        """
        raise NotImplementedError

    def output(self, source_tags: TagResult) -> dict:
        """
        Converts the tagged results into a dictionary format.
        """
        tags = defaultdict(list)
        if source_tags:
            for tag in source_tags.tags:
                tags[f"{self.name}/{tag.name}"].append([tag.start, tag.end, tag.value])

        return tags

    def run_tagger(self, source: T, **kwargs: Any) -> dict:
        """
        Runs a tagger on the given source and returns the results in a dict.
        """
        source_tags = self.tag(source, **kwargs)
        return self.output(source_tags)

    def import_tags(self, imported_tags: list[list[str]]) -> None:
        """
        Imports tags from other experiments.
        """
        taggers = set()
        for experiment in imported_tags:
            for tag_json in experiment:
                tag = json.loads(tag_json)
                if "id" in tag:
                    existing_tags = tag["tags"]
                    for existing_tag in existing_tags:
                        taggers.add(existing_tag.split("/")[0])
                        if existing_tag not in self.imports:
                            self.imports[existing_tag] = {}
                        self.imports[existing_tag].update(
                            {tag["id"]: existing_tags[existing_tag]}
                        )
                else:
                    self.imports["file_tags"] = {tag["source"]: tag["tags"]}

        for dep in self.dependencies:
            if dep not in taggers:
                raise ImportError(
                    f"Missing dependency: {dep}. Imported taggers: {list(taggers)}"
                )


class DocTagger(BaseTagger[Doc]):
    """
    A base class for document taggers.

    This class provides an interface for implementing document tagging functionality.
    Custom document taggers should inherit from this class and implement the tag method.
    """

    @abstractmethod
    def tag(self, source: Doc, **kwargs: Any) -> TagResult:
        raise NotImplementedError


class FileTagger(BaseTagger[File]):
    """
    A base class for file taggers.

    This class provides an interface for implementing file tagging functionality.
    Custom file taggers should inherit from this class and implement the tag method.
    """

    @abstractmethod
    def tag(self, source: File, **kwargs: Any) -> TagResult:
        raise NotImplementedError
