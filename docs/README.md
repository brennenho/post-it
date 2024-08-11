# Post-It Documentation

Install Post-It with `pip`:
```bash
pip install postit
```

## Getting Started
Post-It can be used directly as a command line tool or imported as a Python library. To see available commands, run `postit --help`.

Post-It supports the following tasks:
1. Generating structured data from raw files
2. Processing and applying tags to the structured data
3. Deduplicating the structured data
4. Combining the structured data and tags to create a final corpus

## Index
To learn about each of these steps, please visit their corresponding pages.
- Generating Documents (coming soon)
- Tagging (coming soon)
- Deduplication (coming soon)
- Mixing (coming soon)

## Example
This example uses Post-It as a command line tool to tag and mix the `20 Newsgroups Dataset`. The raw data and all files generated will take `~ 200 MB` of storage.

> [!NOTE]
> Walkthrough this entire example automatically by running `postit example`.

### Download Raw Data
Typically, downloading raw data isn't managed by Post-It. However, for this example you can download the `20 Newsgroups Dataset` by running `postit example --data [DIRECTORY]`. This will download the dataset to a local directory. For the rest of this example, we'll use `example` as our directory.

You should now have the `20 Newsgroups Dataset` downloaded to `example/20news-18828`.

### Generate Documents
The first step is to generate structured data from the raw files. Post-It uses two different terms to describe data:
- `Document`: a single raw file
- `File`: a collection of documents grouped together in a directory

A `File` is stored as a `JSONL` file. Each `Document` in the file is stored as a single line in the following format:
```json
{"id": 0, "source": "path/to/raw/file", "content": "raw text content"}
```

The document generator can be invoked with `postit generate`. Run `postit generate --help` to see the available options.

For this example, run:
 ```bash
 postit generate example/20news-18828/* --output example/documents
 ```
- `example/20news-18828/*`: Path to raw data
    - Use glob patterns. The glob pattern should expand out to a list of subdirectories that will be used for `File` naming.
- `--output example/documents`: Specify the output path (optional)

### Tag Documents
Once Post-It has generated structured data, it can process and tag it as many times as needed. A `Tagger` is a single class that takes a `File` or `Document`, processes it, and applies tags to it.

Each `Tag` has the following values:
- `name`: Intuitive tag name
- `start`: Start of the tag
- `end`: End of the tag
- `value:` Value of the tag. Supported types: `float`, `str`.

For `File` taggers, `start` and `end` correspond to `Document` indexes. For `Document` taggers, they correspond to character ranges within the `content` string of the `Document`.

Taggers can be invoked with `postit tag`. Run `postit tag --help` to see available options.

For this example, we'll use the build-in `doc_length` and `paragraph_length` taggers:
```bash
postit tag length "example/documents/*" --tagger doc_length --tagger paragraph_length
```
- `"example/documents/*"`: Glob path to the structured data
- `--tagger doc_length`: Invoke the `doc_length` tagger
- `--tagger paragraph_length`: Invoke the `paragraph_length` tagger

> [!WARNING]
> Pay attention to the quotation marks around the glob path. Using quotes prevents the shell from expanding the glob path automatically, since Post-It handles this internally. Without the quotation marks, Post-It will still work, but will spawn a bunch of separate processes for each subfolder.

### Deduplication
Under the hood, deduplication uses the same process as tagging. Post-It uses a Bloom Filter to deduplicate at the document or paragraph level.

Deduplication can be run with `postit dedupe`. Run `postit dedupe --help` to see available options.

For this example, let's deduplicate at the document level:
```bash
postit dedupe "example/documents/*" --docs --bloom-file example/bloom.pkl
```

- `"example/documents/*"`: Glob path to the structured data (note the quotes)
- `--docs`: Flag to toggle document-level deduplication
- `--bloom-file example/bloom.pkl`: Path to a Bloom Filter
    - This option can be used to import an existing Bloom Filter
    - If this file doesn't exist, it will be created with the results of this deduplication

### Mixing
After all of the above steps have been completed, Post-It makes it easy to create a final corpus. The `Mixer` combines the structured data with the generated tags while filtering out undesirable tags to create a high-quality dataset.

Mixing can be run with `postit mix`. Run `postit mix --help` to see available options.

Let's use the `doc_length` tagger and deduplication we previously ran. We'll need a `MixerConfig` to tell the mixer what to do. Post-It support `JSON` or `YAML` files.

Create a new file in the `example` directory named `news_config.yml`:
```yml
# example/news_config.yml
name: news-mix
experiments:
  - length
  - dedupe
input_paths:
  - example/documents/*
conditions:
  include:
    - tag: doc_length/num_chars
      operator: '>'
      value: 0
  exclude:
    - tag: doc_dedupe/duplicate
      operator: '>'
      value: 0
```
- `name`: Name of the mix
- `experiments`: Previous tagging/deduplication experiements to import
- `conditions`: Tags to include or exclude while mixing
    - `tag`: Name of the tag. Format: `tagger_name/tag_name`.
    - `operator`: Comparison operator. Valid operators: `in`, `not in`, `==`, `!=`, `>`, `<`, `>=`, `<=`
    - `value`: Value for comparison. Supported types: `float`, `str`, `list`

> [!NOTE]
> Corresponding `.json` file:
> ```json
> {
>    "name": "news-mix",
>    "experiments": ["length", "dedupe"],
>    "input_paths": ["example/documents/*"],
>    "conditions": {
>        "include": [{
>            "tag": "doc_length/num_chars",
>            "operator": ">",
>            "value": 0
>        }],
>        "exclude": [{
>            "tag": "doc_dedupe/duplicate",
>            "operator": ">",
>            "value": 0
>        }]
>    }
> }
> ```

To run the `Mixer`, run:
```bash
postit mix example/news_config.yml
```

The results of the mix will be saved to `example/news-mix/`.