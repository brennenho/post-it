# Deduplication

Under the hood, deduplication uses the same process as tagging. Post-It uses a Bloom Filter to deduplicate at the document or paragraph level.

## Command Line

Deduplication can be invoked with `postit dedupe [PATH TO DOCS] [OPTIONS]`.

Use the following flags to control its behavior:

| Options           | Description
| :------------     | :--------------|
| `--docs`          | Toggle to deduplicate at the document level. |
| `--paragraphs`    | Toggle to deduplicate at the paragraph level. |
| `--experiment`    | Name of the experiment. [default: dedupe] |
| `--bloom-size`    | Size of the bloom filter. [default: 1000000] |
| `--bloom-file`    | Path to a bloom filter .pkl file to import. (ignore to create a new file) |
| `--processes`     | Number of processes to use for parallel processing. [default: 1] |
| `--help`          | Show available options. |

> [!CAUTION]
> Post-It internally expands glob paths. Use quotation marks around glob paths for `[PATH TO DOCS]` (ex: `"example/documents/*"`).

For example, this command will deduplicate at the document level using an existing `bloom.pkl` file with 2 processes:
```bash
postit dedupe "example/documents/*" --docs --bloom-file example/bloom.pkl --processes 2
```

## Package

Post-It's deduper can be incorporated into existing workflows by using it as a package. Deduplication can be initiated using the `Deduper` class:
```python
from postit.deduper import Deduper
```

This class essentially behaves the same as `TaggerProcessor`, with a few modifications unique to deduplication.

> [!TIP]
> Running deduplication doesn't actually remove duplicate data. It tags the duplicate data like any other tagger, and will remove duplicates at during [Mixing](mixing.md).

Use `Deduper.dedupe()` as the entrypoint:
```python
def dedupe(
        glob_paths: list[str],
        experiment: str = "dedupe",
        dedupe_docs: bool = False,
        dedupe_paragraphs: bool = False,
        bloom_size: int = 1000000,
        bloom_file: str = "",
        num_processes: int = 1,
        **kwargs: Any,
    ):
```

| Parameters            | Description
| :------------         | :--------------|
| `glob_paths`          | List of file paths to raw data. Glob patterns supported. |
| `experiment`          | Name of the experiment. |
| `dedupe_docs`         | Toggle to deduplicate at the document level. |
| `dedupe_paragraphs`   | Toggle to deduplicate at the paragraph level. |
| `bloom_size`          | Size of the bloom filter (if creating a filter). |
| `bloom_file`          | Path to a bloom filter .pkl file to import (leave blank to create a new file). |
| `num_processes`       | The # of parallel processes to run. |
| `**kwargs`            | Any number of optional parameters you would like passed directly to taggers. |

### See next: [Mixing](mixing.md)