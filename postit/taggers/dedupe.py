from postit.registry import tagger
from postit.tagging import DocTagger, TagResult
from postit.types import Doc, FloatTag, Tag
from postit.utils.bloom import BloomFilter


@tagger
class DocDedupe(DocTagger):
    name = "doc_dedupe"

    def tag(self, source: Doc, **kwargs) -> TagResult:
        bloom: BloomFilter = kwargs.get("bloom", None)
        if not bloom:
            raise ValueError("Bloom filter not provided.")

        tags: list[Tag] = []
        clean_doc = source.content.strip().lower()
        if clean_doc in bloom:
            tags.append(
                FloatTag(name="duplicate", start=0, end=len(source.content), value=1)
            )
        else:
            bloom.add(clean_doc)

        return TagResult(source, tags)


@tagger
class ParagraphDedupe(DocTagger):
    name = "paragraph_dedupe"

    def tag(self, source: Doc, **kwargs) -> TagResult:
        bloom: BloomFilter = kwargs.get("bloom", None)
        if not bloom:
            raise ValueError("Bloom filter not provided.")

        tags: list[Tag] = []
        start = 0
        for paragraph in source.content.split("\n"):
            clean_paragraph = paragraph.strip().lower()
            if clean_paragraph in bloom:
                tags.append(
                    FloatTag(
                        name="duplicate",
                        start=start,
                        end=start + len(paragraph),
                        value=1,
                    )
                )
            else:
                bloom.add(clean_paragraph)
            start += len(paragraph) + 1

        return TagResult(source, tags)
