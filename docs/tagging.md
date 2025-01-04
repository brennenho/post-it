# Tagging

> [!IMPORTANT]
> [Generating Documents](documents.md) must occur prior to tagging. See [Custom Taggers](custom-taggers.md) for how to define your own taggers.

Tagging is Post-It's core functionality. Using structured data, Post-It can process and label it as many times as needed. A `Tagger` is a single Python class that takes either a `File` or `Document`, process it, and applies "tags" to the data.

A `Tag` represents metadata about the data (such as character count). Each `Tag` can be used to filter undesirable data at the mixing stage.

Each `Tag` has the following values:
| Value         | Description
| :------------ | :--------------|
| `name`        | Intuitive tag name |
| `start`       | Start of the tag (number of characters from the start of the `Document`) |
| `end`         | End of the tag (number of characters from the start of the `Document`) |
| `value`       | The metadata stored in the tag (supported types: `float` or `str`) |

> [!IMPORTANT]
> For `File` taggers, `start` and `end` correspond to `Document` indexes. For `Document` taggers, they correspond to character ranges from the start of `Document`.

## Taggers
A Tagger is simply a custom function that executes on a `File` or `Document` and returns a list of `Tag` objects. The Post-It framework handles parallelizing the dataset, calling a tagger, and saving its results.

Post-It has some built-in taggers that provide frequently used functionality:

| Tagger                | Type      | Description
| :------------         | :-------  | :-------------- |
| `doc_length`          | Document  | Calculates the number of words/characters in a document. |
| `paragraph_length`    | Document  | Calculates the number of words/characters in each paragraph of a document. |
| `doc_lines`           | Document  | Calculates the number of lines in a document. |
| `num_docs`            | File      | Calculates the number of documents in a file. |

## Command Line

Built-in taggers can be invoked from the command line with `postit tag [EXPERIMENT] [PATH TO DOCS] [OPTIONS]`.

> [!IMPORTANT]
> Since multiple taggers can be run at the same time, Post-It uses experiments to combine multiple taggers into a single run. Experiments can be named anything and the tagging metadata produced from the execution will all be stored in the same files.

Use the following flags to control its behavior:

| Options           | Description
| :------------     | :--------------|
| `--tagger`        | Names of taggers to run (use this option as many times as needed). |
| `--processes`     | Number of processes to use for parallel processing. [default: 1] |
| `--help`          | Show available options. |

> [!CAUTION]
> Post-It internally expands glob paths. Use quotation marks around glob paths for `[PATH TO DOCS]` (ex: `"example/documents/*"`).

For example, we can create a `length` experiment executing the `doc_length` and `paragraph_length` taggers with 2 processes:
```bash
postit tag length "example/documents/*" --tagger doc_length --tagger paragraph_length --processes 2
```

## Package

Incorporate Post-It into unique workflows by using it as a package. Tagging is managed by `TaggerProcessor`:
```python
from postit.processor import TaggerProcessor
```

This class handles calling specified taggers while providing parallelization and logging functionality.

Use `TaggerProcessor.tag()` as the entrypoint:
```python
def tag(
        glob_paths: list[str],
        tagger_names: list[str],
        experiment: str,
        imported_experiments: list[str] = [],
        num_processes: int = 1,
        **kwargs: Any,
    ):
```

| Parameters            | Description
| :------------         | :--------------|
| `glob_paths`          | List of file paths to raw data. Glob patterns supported. |
| `tagger_names`        | List of string names of taggers to run. |
| `experiment`          | Name of the experiment. |
| `imported_experiments`| List of previous experiments to import (if previous data is needed in current experiment). |
| `num_processes`       | The # of parallel processes to run. |
| `**kwargs`            | Any number of optional parameters you would like passed directly to taggers (ex: a global bloom filter). |

### See next: [Custom Taggers](custom-taggers.md)