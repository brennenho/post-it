import re

from postit.registry import tagger
from postit.tagging import DocTagger, TagResult
from postit.types import Doc, FloatTag, Tag


@tagger
class CodeComments(DocTagger):
    """
    Tag comment blocks in code.
    Supported symbols: `#`, `//`, `/* .. */`, `<!-- .. -->`
    Derive this class to add support for other symbols.

    Example:
        .. code-block :: python

            @tagger
            class CustomComments(CodeComments):
                name = "custom_comments"
                single_line_symbols = ["DEFINE HERE"]

                def tag(self, doc: Doc) -> TagResult:
                    return super().tag(doc)
    """

    name = "code_comments"
    single_line_symbols: list[str] = ["#", "//"]
    multi_line_symbols: list[tuple[str, str]] = [("/*", "*/"), ("<!--", "-->")]

    def tag(self, source: Doc, **kwargs) -> TagResult:
        escaped_single = [re.escape(symbol) for symbol in self.single_line_symbols]
        escaped_multi = [
            (re.escape(start), re.escape(end)) for start, end in self.multi_line_symbols
        ]

        # Identify strings to avoid matching comment chars within them
        string_pattern = r"(?:(?<!\\)\"(?:\\.|[^\"\\])*\"|(?<!\\)'(?:\\.|[^'\\])*')"

        # Comment patterns
        single_pattern = r"|".join(
            [
                symbol + r"[^\n]*(?:\n" + symbol + r"[^\n]*)*"
                for symbol in escaped_single
            ]
        )
        multi_pattern = r"|".join(
            [start + r"(.*?)" + end for start, end in escaped_multi]
        )

        comment_pattern = rf"(?:{string_pattern})|({single_pattern})|({multi_pattern})"

        comments = [
            (match.start(match.lastindex), match.end(match.lastindex))
            for match in re.finditer(
                comment_pattern, source.content, re.MULTILINE | re.DOTALL
            )
            if match.lastindex
        ]

        tags: list[Tag] = [
            FloatTag("comments", start, end, 1) for start, end in comments
        ]

        return TagResult(source, tags)


@tagger
class CodeLicenses(DocTagger):
    """
    Tag comment blocks that contain license information.
    `code_comments` tagger must be run before this tagger.
    """

    name = "code_licenses"
    dependencies = ["code_comments"]

    def tag(self, source: Doc, **kwargs) -> TagResult:
        license_pattern = re.compile(
            r"\b(copyright|license|licensed|all rights reserved)", re.IGNORECASE
        )

        # Import tagged comment blocks from the `code_comments` tagger
        comments = self.imports.get("code_comments/comments", {}).get(source.id, [])
        tags: list[Tag] = [
            FloatTag("notice", start, end, 1)
            for start, end, _ in comments
            if license_pattern.search(source.content[start:end])
        ]

        return TagResult(source, tags)
