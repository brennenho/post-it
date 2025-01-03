## Generating Documents

Post-It does not handle raw data collection. In order to use this package, you must have your raw data files saved to one of the following locations:

- a local machine (where you are planning on running Post-It)
- a Google Cloud Storage bucket
- an Amazon S3 bucket (not currently supported)

The first step is to generate structured data from the raw files. Post-It uses two different terms to describe data:
- `Document`: a single raw file
- `File`: a collection of documents grouped together in a directory

> [!NOTE]
> Think about `Document`s as source code and a `File` as a single GitHub repository if you were curating a code dataset.

A `File` is stored as a `JSONL` file. Each `Document` in the file is stored as a single line in the following format:
```json
{"id": 0, "source": "path/to/raw/file", "content": "raw text content"}
{"id": 1, "source": "path/to/raw/file", "content": "raw text content"}
...
```

## CLI

The document generator can be invoked with `postit generate [PATH TO RAW DATA] [OPTIONS]`. Use the following options flags to control its behavior:

| Options           | Description
| :------------     | :--------------|
| `--output`        | Path to output directory. [default: `./documents`] |
| `--no-keep-raw`   | Don't keep raw files after generating documents. |
| `--processes`     | Number of processes to use for parallel processing. [default: 1] |
| `--help`          | Show available options. |

For example, let's assume your raw data is stored in the relative path `./raw_data`. You can convert this raw data into `Document`s using 2 processes with this command:
```bash
postit generate raw_data/* --processes 2
```

> [!WARNING]
> The path you specify is important! The trailing `*` glob pattern ensures your sub-folders are converted into individual `File`s.

Your `.jsonl` files will be stored at `./documents` (or the `--output` path you specified). This folder will be used in subsequent steps.

## Package

If you want to build this functionality into other workflows, you can also use Post-It as a Python package. Import the `DocumentGenerator`:
```python
from postit.documents import DocumentGenerator
```

Use `DocumentGenerator.generate()` to execute the conversion process:
```python
def generate(
        folder_paths: list[str],
        output_path: str = "./documents",
        keep_raw: bool = True,
        num_processes: int = 1,
    ):
```

| Parameters        | Description
| :------------     | :--------------|
| `folder_paths`    | Glob pattern to the raw data. |
| `output_path`     | Relative path to output directory (will be created if it doesn't exist). |
| `keep_raw`        | Set flag to `False` to delete raw data. |
| `num_processes`   | The # of parallel processes to run. |