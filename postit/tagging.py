import json

from abc import ABC, abstractmethod
from collections import defaultdict
from postit.types import Doc, File, Source, TagResult
from typing import Generic, TypeVar

T = TypeVar("T", bound="Source")


class BaseTagger(ABC, Generic[T]):
    """
    Base class for taggers.

    This class defines the common interface and behavior for taggers.
    DocTagger and FileTagger classes are inherited from this class.
    NOTE: Do not inherit from this class directly. Inherit from DocTagger or FileTagger instead.

    Attributes:
        name (str): The name of the tagger.
        dependencies (list[str]): The list of tagger dependencies.
        imports (dict[str, dict]): The imported tags from other experiments.
            This is generated automatically by the processor. You should not need to modify this.

    Methods:
        tag(source: T) -> TagResult: Performs the tagging operation on the given source.
        output(source_tags: TagResult) -> list: Converts the tagged results into a list format.
        run_tagger(source: T) -> tuple[str, list]: Runs the tagger on the given source and returns the name and output.
        import_tags(imported_tags: list[str]) -> None: Imports tags from other experiments.
    """

    name: str
    dependencies: list[str] = []
    imports: dict[str, dict] = {}

    @abstractmethod
    def tag(self, source: T) -> TagResult:
        """
        Tags the given source object and returns the result.
        This method should be overridden by custom taggers.

        Args:
            source (T): The source object to be tagged.

        Returns:
            TagResult: The result of the tagging operation.
        """
        raise NotImplementedError

    def output(self, source_tags: TagResult, exp: str) -> dict:
        """
        Converts the tagged results into a dictionary format.

        Args:
            source_tags (TagResult): The source_tags to be converted.
            exp (str): The experiment name.

        Returns:
            dict: A dictionary of the tagged results.
                Keys are in the format: `[experiment name]_[tagger name]_[tag name]`.
                Values are in the format: `[start, end, value]` for each tag.
        """
        tags = defaultdict(list)
        if source_tags:
            for tag in source_tags.tags:
                tags[f"{self.name}/{tag.name}"].append([tag.start, tag.end, tag.value])

        return tags

    def run_tagger(self, source: T, exp: str) -> dict:
        """
        Runs a tagger on the given source and returns the results in a dict.

        Args:
            source (T): The source to be tagged. Should be a Doc or File object.

        Returns:
            dict: A dictonary of the tagged results.
        """
        source_tags = self.tag(source)
        return self.output(source_tags, exp)

    def import_tags(self, imported_tags: list[list[str]]) -> None:
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


class DocTagger(BaseTagger):
    """
    A base class for document taggers.

    This class provides an interface for implementing document tagging functionality.
    Custom document taggers should inherit from this class and implement the tag method.
    """

    @abstractmethod
    def tag(self, doc: Doc) -> TagResult:
        raise NotImplementedError


class FileTagger(BaseTagger):
    """
    A base class for file taggers.

    This class provides an interface for implementing file tagging functionality.
    Custom file taggers should inherit from this class and implement the tag method.
    """

    @abstractmethod
    def tag(self, file: File) -> TagResult:
        raise NotImplementedError
