# Custom Taggers

Post-It is designed to be extended. It is easy to define custom taggers to adapt Post-It to fit unique workflows.

## Document Tagger
Use the following code as a template:

```python
from postit.registry import tagger
from postit.tagging import DocTagger, TagResult
from postit.types import Doc, FloatTag, StrTag, Tag


@tagger  # Decorator registers class as a Tagger with Post-It
class ExampleTagger(DocTagger):
    """
    An example of how to define a custom Document tagger.
    """

    name = "example_tagger"  # Define string name of the tagger to be used elsewhere

    # Override the tag() function from DocTagger
    def tag(self, source: Doc, **kwargs) -> TagResult:
        tags: list[Tag] = []
        tags.append(
            FloatTag(
                name="ex_tag_1",
                start=0,
                end=len(source.content),
                value=0,  # Set tag value here
            )
        )
        tags.append(
            StrTag(
                name="ex_tag_2",
                start=0,
                end=len(source.content),
                value="test",  # Set tag value here
            )
        )
        return TagResult(source, tags)
```

In this example, both the `FloatTag` and `StrTag` span the entire Document (specified by their `start` and `end` values).

## File Tagger
Use the following code as a template. It shares many similarities to the above `Document` tagger.

```python
from postit.registry import tagger
from postit.tagging import FileTagger, TagResult
from postit.types import File, FloatTag, Tag

@tagger
class ExampleTagger(FileTagger):
    """
    An example of how to define a custom File tagger.
    """

    name = "example_tagger"

    def tag(self, source: File, **kwargs) -> TagResult:
        tags: list[Tag] = [
            FloatTag(
                name="ex_tag",
                start=0,
                end=len(source.content),
                value=0,  # Set tag value here
            )
        ]
        return TagResult(source, tags)
```

In this example, `source.content` is a list of `Doc` objects. This tag spans all `Document`s in this `File`.

### See next: [Deduplication](deduplication.md)