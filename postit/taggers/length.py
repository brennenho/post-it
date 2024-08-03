from postit.registry import tagger
from postit.tagging import DocTagger, FileTagger, TagResult
from postit.types import Doc, File, FloatTag, Tag


@tagger
class DocLength(DocTagger):
    """
    Calculates the number of words/characters in a document.
    """

    name = "doc_length"

    def tag(self, doc: Doc) -> TagResult:
        tags: list[Tag] = []
        tags.append(
            FloatTag(
                name="num_chars", start=0, end=len(doc.content), value=len(doc.content)
            )
        )
        tags.append(
            FloatTag(
                name="num_words",
                start=0,
                end=len(doc.content),
                value=len(doc.content.split()),
            )
        )
        return TagResult(doc, tags)


@tagger
class ParagraphLength(DocTagger):
    """
    Calculates the number of words/characters in each paragraph of a document.
    """

    name = "paragraph_length"

    def tag(self, doc: Doc) -> TagResult:
        tags: list[Tag] = []
        start = 0
        for paragraph in doc.content.split("\n"):
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
        return TagResult(doc, tags)


@tagger
class DocLines(DocTagger):
    """
    Calculates the number of lines in a document.
    """

    name = "doc_lines"

    def tag(self, doc: Doc) -> TagResult:
        tags: list[Tag] = []
        lines = doc.content.split("\n")
        tags.append(FloatTag("num_lines", 0, len(doc.content), len(lines)))
        tags.append(
            FloatTag(
                "avg_chars_per_line", 0, len(doc.content), len(doc.content) / len(lines)
            )
        )
        tags.append(
            FloatTag("max_lines", 0, len(doc.content), max(len(line) for line in lines))
        )
        return TagResult(doc, tags)


@tagger
class NumDocs(FileTagger):
    """
    Calculates the number of documents in a file.
    """

    name = "num_docs"

    def tag(self, file: File) -> TagResult:
        tags: list[Tag] = []
        tags.append(
            FloatTag(
                name="total_docs",
                start=0,
                end=len(file.content),
                value=len(file.content),
            )
        )
        return TagResult(file, tags)
