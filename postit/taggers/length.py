from postit.registry import tagger
from postit.tagging import DocTagger, FileTagger, TagResult
from postit.types import Doc, File, FloatTag, Tag


@tagger
class DocLength(DocTagger):
    """
    Calculates the number of words/characters in a document.
    """

    name = "doc_length"

    def tag(self, source: Doc, **kwargs) -> TagResult:
        tags: list[Tag] = []
        tags.append(
            FloatTag(
                name="num_chars",
                start=0,
                end=len(source.content),
                value=len(source.content),
            )
        )
        tags.append(
            FloatTag(
                name="num_words",
                start=0,
                end=len(source.content),
                value=len(source.content.split()),
            )
        )
        return TagResult(source, tags)


@tagger
class ParagraphLength(DocTagger):
    """
    Calculates the number of words/characters in each paragraph of a document.
    """

    name = "paragraph_length"

    def tag(self, source: Doc, **kwargs) -> TagResult:
        tags: list[Tag] = []
        start = 0
        for paragraph in source.content.split("\n"):
            end = start + len(paragraph)
            tags.append(
                FloatTag(name="num_chars", start=start, end=end, value=len(paragraph))
            )
            tags.append(
                FloatTag(
                    name="num_words", start=start, end=end, value=len(paragraph.split())
                )
            )
            start = end + 1
        return TagResult(source, tags)


@tagger
class DocLines(DocTagger):
    """
    Calculates the number of lines in a document.
    """

    name = "doc_lines"

    def tag(self, source: Doc, **kwargs) -> TagResult:
        tags: list[Tag] = []
        lines = source.content.split("\n")
        tags.append(FloatTag("num_lines", 0, len(source.content), len(lines)))
        tags.append(
            FloatTag(
                "avg_chars_per_line",
                0,
                len(source.content),
                len(source.content) / len(lines),
            )
        )
        tags.append(
            FloatTag(
                "max_lines", 0, len(source.content), max(len(line) for line in lines)
            )
        )
        return TagResult(source, tags)


@tagger
class NumDocs(FileTagger):
    """
    Calculates the number of documents in a file.
    """

    name = "num_docs"

    def tag(self, source: File, **kwargs) -> TagResult:
        tags: list[Tag] = [
            FloatTag(
                name="total_docs",
                start=0,
                end=len(source.content),
                value=len(source.content),
            )
        ]
        return TagResult(source, tags)
