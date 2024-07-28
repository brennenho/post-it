from abc import ABC, abstractmethod
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

    Methods:
        tag(source: T) -> TagResult: Performs the tagging operation on the given source.
        output(source_tags: TagResult) -> list: Converts the tagged results into a list format.
        run_tagger(source: T) -> tuple[str, list]: Runs the tagger on the given source and returns the name and output.
    """

    @property
    def name(self) -> str:
        return self.__class__.__name__

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

    def output(self, source_tags: TagResult) -> list:
        """
        Converts the given source_tags into a list of lists containing the start index, end index, and value of each tag.

        Args:
            source_tags (TagResult): The source_tags to be converted.

        Returns:
            list: A list of lists, where each inner list contains the start index, end index, and value of a tag.
        """
        output = []
        for tag in source_tags.tags:
            output.append([tag.start, tag.end, tag.value])
        return output

    def run_tagger(self, source: T) -> tuple[str, list]:
        """
        Runs the tagger on the given source and returns a tuple containing the name of the tagger and the tagged source.

        Args:
            source (T): The source to be tagged.

        Returns:
            tuple[str, list]: A tuple containing the name of the tagger and the tagged source.
        """
        source_tags = self.tag(source)
        return (self.name, self.output(source_tags))


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
