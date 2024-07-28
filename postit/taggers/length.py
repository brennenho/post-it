from postit.registry import tagger
from postit.tagging import DocTagger, FileTagger, TagResult
from postit.types import Doc, File, FloatTag, Tag


@tagger
class DocLengthChars(DocTagger):
    def tag(self, doc: Doc) -> TagResult:
        spans: list[Tag] = []
        spans.append(FloatTag(0, len(doc.content), len(doc.content)))
        return TagResult(doc, spans)


@tagger
class ParagraphLengthChars(DocTagger):
    def tag(self, doc: Doc) -> TagResult:
        spans: list[Tag] = []
        start = 0
        for paragraph in doc.content.split("\n"):
            end = start + len(paragraph)
            spans.append(FloatTag(start, end, len(paragraph)))
            start = end + 1
        return TagResult(doc, spans)


@tagger
class NumDocs(FileTagger):
    def tag(self, file: File) -> TagResult:
        spans: list[Tag] = []
        spans.append(FloatTag(0, len(file.content), len(file.content)))
        return TagResult(file, spans)
