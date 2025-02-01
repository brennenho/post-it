import os
import tarfile

from postit.deduper import Deduper
from postit.documents import DocumentGenerator
from postit.mixer import Condition, Mixer, MixerConfig
from postit.processor import TaggerProcessor
from rich import print
from rich.markdown import Markdown
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
)
from urllib.request import urlretrieve


def download_20newsgroups_raw(progress: Progress, task, data_dir):
    url = "https://github.com/brennenho/post-it/raw/refs/heads/main/docs/assets/20_newsgroups.tar.gz"
    tar_filename = os.path.join(data_dir, "20_newsgroups.tar.gz")

    os.makedirs(data_dir, exist_ok=True)

    if not os.path.exists(tar_filename):
        progress.update(task, description="[yellow]Downloading tar file...", advance=50)
        urlretrieve(url, tar_filename)

    # Extract the tar file with the custom filter to avoid deprecation warning
    with tarfile.open(tar_filename, "r:gz") as tar:
        progress.update(task, description="[yellow]Extracting tar file...")
        tar.extractall(path=data_dir)

    # Remove the tar file
    os.remove(tar_filename)
    progress.update(task, description="[green]Download complete.", advance=50)


def download_data(data_dir):
    with Progress(
        TextColumn(
            "[progress.description]{task.description}",
        ),
        SpinnerColumn(),
        transient=True,
    ) as progress:
        task = progress.add_task("[yellow]Initiating download...", total=100)
        download_20newsgroups_raw(progress, task, data_dir)

    print(f"Successfully downloaded dataset to {data_dir}/20_newsgroups.")


def news_example(data_dir="example"):
    md = f"""
    Example: 20 Newsgroups Dataset
    --------------------------------
    This example runs the full PostIt pipeline on the 20 Newsgroups dataset.
    Steps:
        1. Generate documents from raw data.
        2. Tag documents with `doc_length` and `paragraph_length` taggers.
        3. Deduplicate documents.
        4. Mix documents based on length and deduplication tags.
    
    All data from this example will be stored in the `{data_dir}` directory.
"""
    print(Markdown(md))
    download_data(data_dir)

    print("Continue? (return)")
    input()

    print("Generating documents from raw data. Equivalent CLI command:")
    print(
        Markdown(
            f"```md\npostit generate {data_dir}/20_newsgroups/* --output {data_dir}/documents\n```"
        )
    )
    DocumentGenerator.generate(
        folder_paths=[f"{data_dir}/20_newsgroups/*"],
        output_path=f"{data_dir}/documents",
    )
    print("Continue? (return)")
    input()

    print(
        "Tagging documents with doc_length and paragraph_length taggers. Equivalent CLI command:"
    )
    print(
        Markdown(
            f'```md\npostit tag length "{data_dir}/documents/*" --tagger doc_length --tagger paragraph_length\n```'
        )
    )
    TaggerProcessor.tag(
        glob_paths=[f"{data_dir}/documents/*"],
        tagger_names=["doc_length", "paragraph_length"],
        experiment="length",
    )
    print("Continue? (return)")
    input()

    print("Deduplicating documents. Equivalent CLI command:")
    print(
        Markdown(
            f'```md\npostit dedupe "{data_dir}/documents/*" --docs --bloom-file {data_dir}/bloom.pkl\n```'
        )
    )
    Deduper.dedupe(
        glob_paths=[f"{data_dir}/documents/*"],
        experiment="dedupe",
        dedupe_docs=True,
        bloom_file=f"{data_dir}/bloom.pkl",
    )
    print("Continue? (return)")
    input()

    print(
        "Mixing documents based on length and deduplication tags. Equivalent CLI command:"
    )
    print(Markdown(f"```md\npostit mix {data_dir}/news_config.json\n```"))
    mixer_config = MixerConfig(
        name="news-mix",
        experiments=["length", "dedupe"],
        input_paths=[f"{data_dir}/documents/*"],
        conditions={
            "include": [
                Condition(tag="doc_length/num_chars", operator=">", value=0),
            ],
            "exclude": [
                Condition(tag="doc_dedupe/duplicate", operator=">", value=0),
            ],
        },
    )
    mixer_config.save(f"{data_dir}/news_config.json")
    Mixer.mix(mixer_config)
    print(f"Example complete. See all results in the `{data_dir}` directory.")
