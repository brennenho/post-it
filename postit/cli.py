import typer

from postit.deduper import Deduper
from postit.documents import DocumentGenerator
from postit.examples.news import download_data, news_example
from postit.mixer import Mixer, MixerConfig
from postit.processor import TaggerProcessor
from typing import Annotated

app = typer.Typer(no_args_is_help=True, rich_markup_mode="rich")


@app.callback()
def callback():
    """
    PostIt: A robust, extensible Python data tagging framework for dynamic processing and intelligent filtering of pretraining corpora for AI models.
    """


@app.command()
def generate(
    paths: Annotated[
        list[str],
        typer.Argument(
            help="List of file paths to raw data. Glob patterns supported.",
            show_default=False,
        ),
    ],
    output: Annotated[
        str,
        typer.Option(help="Path to output directory."),
    ] = "./documents",
    keep_raw: Annotated[
        bool,
        typer.Option(help="Keep raw files after generating documents."),
    ] = True,
    processes: Annotated[
        int,
        typer.Option(help="Number of processes to use for parallel processing."),
    ] = 1,
):
    """
    Generate documents from raw data files.
    """
    DocumentGenerator.generate(
        folder_paths=paths,
        output_path=output,
        keep_raw=keep_raw,
        num_processes=processes,
    )


@app.command()
def tag(
    experiment: Annotated[
        str,
        typer.Argument(help="Name of the experiment.", show_default=False),
    ],
    paths: Annotated[
        list[str],
        typer.Argument(
            help="List of file paths to raw data. Glob patterns supported.",
            show_default=False,
        ),
    ],
    tagger: Annotated[
        list[str],
        typer.Option(help="Names of taggers to run.", show_default=False),
    ],
    processes: Annotated[
        int,
        typer.Option(help="Number of processes to use for parallel processing."),
    ] = 1,
):
    """
    Tag documents with specified taggers.
    """
    TaggerProcessor.tag(
        glob_paths=paths,
        tagger_names=tagger,
        experiment=experiment,
        num_processes=processes,
    )


@app.command()
def dedupe(
    paths: Annotated[
        list[str],
        typer.Argument(
            help="List of file paths to raw data. Glob patterns supported.",
            show_default=False,
        ),
    ],
    docs: Annotated[
        bool,
        typer.Option(help="Toggle to deduplicate at the document level."),
    ] = False,
    paragraphs: Annotated[
        bool,
        typer.Option(help="Toggle to deduplicate at the paragraph level."),
    ] = False,
    experiment: Annotated[
        str,
        typer.Option(help="Name of the experiment."),
    ] = "dedupe",
    bloom_size: Annotated[
        int,
        typer.Option(help="Size of the bloom filter."),
    ] = 1000000,
    bloom_file: Annotated[
        str,
        typer.Option(help="Path to a bloom filter .pkl file to import."),
    ] = "",
    processes: Annotated[
        int,
        typer.Option(help="Number of processes to use for parallel processing."),
    ] = 1,
):
    """
    Deduplicate documents at the document or paragraph level.
    """
    Deduper.dedupe(
        glob_paths=paths,
        experiment=experiment,
        dedupe_docs=docs,
        dedupe_paragraphs=paragraphs,
        bloom_size=bloom_size,
        bloom_file=bloom_file,
        num_processes=processes,
    )


@app.command()
def mix(
    config: Annotated[
        str,
        typer.Argument(
            help="Path to the mixer configuration file. Supported formats: .json, .yaml, .yml.",
            show_default=False,
        ),
    ],
    processes: Annotated[
        int,
        typer.Option(help="Number of processes to use for parallel processing."),
    ] = 1,
):
    """
    Mix documents based on specified conditions.
    """
    mixer_config = MixerConfig.load(config)
    Mixer.mix(mixer_config, processes)


@app.command()
def example(
    directory: Annotated[
        str,
        typer.Argument(
            help="Path to working directory for the example.",
        ),
    ] = "example",
    data: Annotated[
        bool,
        typer.Option(
            help="Download example data only.",
        ),
    ] = False,
):
    """
    Run the example news processing pipeline.
    """
    if data:
        download_data(directory)
    else:
        news_example(directory)
