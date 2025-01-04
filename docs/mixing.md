# Mixing

After generating documents, running taggers, and (optionally) deduplicating data, the final step is to combine the generated metadata into a final dataset. Running taggers only needs to happen once to generate the metadata. Tags can be mixed into a final dataset as many times as desired.

The `Mixer` combines the structured data of `Document`s with the generated tagging data while filtering out undesirable tags to create a high quality final dataset.

## Configuration

There are a variety of options that can be tweaked during the mixing process to achieve a desired final result:

- `name`: Name of the mix
- `experiments`: Previous tagging/deduplication experiments to import
- `conditions`: Tags to include or exclude while mixing
    - `tag`: Name of the tag. Format: `tagger_name/tag_name`.
    - `operator`: Comparison operator. Valid operators: `in`, `not in`, `==`, `!=`, `>`, `<`, `>=`, `<=`
    - `value`: Value for comparison. Supported types: `float`, `str`, `list`


These options are passed to the `Mixer` in a `.json`, `.yaml`, or `.yml` file. Example `.yml` configuration:

```yml
# example.yml
name: example-mix
experiments:
- example_exp_1
- example_exp_2
input_paths:
- example/documents/*
conditions:
include:
    - tag: example_tagger/example_tag_1
    operator: '>'
    value: 0
exclude:
    - tag: example_tagger/example_tag_2
    operator: '<'
    value: 0
```

> [!TIP]
> Example configuration files: [example-config.yml](example-config.yml) and [example-config.json](example-config.json)

## Command Line

Mixing can be initiated from the command line with `postit mix [PATH TO CONFIG] [OPTIONS]`.

Use the following flags to control its behavior:

| Options           | Description
| :------------     | :--------------|
| `--processes`     | Number of processes to use for parallel processing. [default: 1] |
| `--help`          | Show available options. |

## Package

Mixing can be incorporated as a package by importing `Mixer` and `MixerConfig`:
```python
from postit.mixer import Mixer, MixerConfig
```

`MixerConfig` mirrors the configuration options listed above. Either define a `MixerConfig` object manually or use `MixerConfig.load(path)` to load a configuration from a file in the provided format.

To initiate the mixing process, use `Mixer.mix()`:
```python
def mix(config: MixerConfig, num_processes: int = 1) -> None:
```

| Parameters            | Description
| :------------         | :--------------|
| `config`              | `MixerConfig` object previously created or loaded. |
| `num_processes`       | The # of parallel processes to run. |
