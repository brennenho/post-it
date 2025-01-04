import concurrent.futures

from concurrent.futures import ThreadPoolExecutor
from postit.files import FileClient
from postit.registry import TaggerRegistry
from postit.tagging import DocTagger, FileTagger
from postit.types import File
from postit.utils.logging import get_logger
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
    TimeElapsedColumn,
)
from rich.table import Column
from typing import Any

# TODO: improve error handling


class BaseProcessor:
    """
    Abstract base class for processing files in parallel.
    """

    label: str = "Processing"
    units: str = "files"

    def __init__(self, num_processes: int = 1, logger=None):
        self.num_processes = num_processes
        self.progress = Progress(
            TextColumn(
                "[progress.description]{task.description}",
                table_column=Column(width=22),
            ),
            SpinnerColumn(table_column=Column(width=1)),
            BarColumn(),
            TaskProgressColumn(table_column=Column(width=5)),
            TextColumn("|", table_column=Column(width=1)),
            MofNCompleteColumn(table_column=Column(width=15)),
            TextColumn(f"[green]{self.units}", table_column=Column(width=5)),
            TextColumn("|", table_column=Column(width=1)),
            TimeElapsedColumn(table_column=Column(width=8)),
            TextColumn("[yellow]elapsed", table_column=Column(width=6)),
        )
        self.logger = logger or get_logger(__name__)

    def process(self, *args, **kwargs):
        """
        Abstract method to process a single file. Implemented by subclasses.
        """
        raise NotImplementedError

    def run(self, paths: list[str], **kwargs: Any):
        """
        Runs the processing on multiple paths in parallel using ThreadPoolExecutor.
        """
        with self.progress:
            self.task = self.progress.add_task(f"[yellow]{self.label}", total=None)
            total = self.get_total(paths, **kwargs)
            self.progress.update(self.task, total=total)
            self.logger.info(
                f"Processing {total} {self.units} using {self.num_processes} processes."
            )
            with ThreadPoolExecutor(max_workers=self.num_processes) as executor:
                futures = {executor.submit(self.process, path): path for path in paths}

                results = []
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())

                self.progress.update(
                    self.task,
                    description=f"[green]:heavy_check_mark: {self.label}",
                )
                return results

    def get_total(self, paths: list[str], **kwargs: Any) -> int:
        """
        Returns the total number of files to process.
        This method should be overridden by subclasses, depending on total number of steps required.
        """
        return len(paths)


class TaggerProcessor(BaseProcessor):
    """
    Tags documents using taggers in parallel.
    One file is processed per thread at a time.

    Use TaggerProcessor.tag() as the entry point.
    """

    label = "Tagging"
    units = "tags"

    @staticmethod
    def tag(
        glob_paths: list[str],
        tagger_names: list[str],
        experiment: str,
        imported_experiments: list[str] = [],
        num_processes: int = 1,
        **kwargs: Any,
    ):
        """
        Tag documents using taggers.

        Args:
            glob_paths (list[str]): List of glob patterns for the documents to tag.
            tagger_names (list[str]): List of tagger names to be used.
            experiment (str): Name of the experiment.
            imported_experiments (list[str], optional): List of imported experiment names. Defaults to [].
            num_processes (int, optional): Number of processes to use for parallel processing. Defaults to 1.
        """
        TaggerProcessor.label = f"Tagging ({experiment})"
        for glob_path in glob_paths:
            file_client = FileClient.get_for_target(glob_path)
            document_paths = file_client.glob(glob_path)
            processor = TaggerProcessor(
                tagger_names=tagger_names,
                experiment=experiment,
                file_client=file_client,
                imported_experiments=imported_experiments,
                num_processes=num_processes,
                **kwargs,
            )
            processor.run(document_paths, num_taggers=len(tagger_names))

    def __init__(
        self,
        tagger_names: list[str],
        experiment: str,
        file_client: FileClient,
        imported_experiments: list[str] = [],
        num_processes: int = 1,
        **kwargs: Any,
    ):
        super().__init__(num_processes)
        self.experiment = experiment
        self.file_client = file_client
        self.imported_experiments = imported_experiments
        self.kwargs = kwargs

        self.doc_taggers: list[DocTagger] = []
        self.file_taggers: list[FileTagger] = []
        taggers = [TaggerRegistry.get(tagger)() for tagger in tagger_names]

        for tagger in taggers:
            if isinstance(tagger, DocTagger):
                self.doc_taggers.append(tagger)
            elif isinstance(tagger, FileTagger):
                self.file_taggers.append(tagger)
            else:
                raise ValueError(f"Unknown tagger type: {tagger}")

    def process(self, path: str):
        file = File.from_raw(path, self.file_client.read(path))
        imported_tags = []
        for imported_experiment in self.imported_experiments:
            imported_tags.append(
                self.file_client.read(
                    path.replace("documents", f"tags/{imported_experiment}")
                )
                .strip()
                .splitlines()
            )

        for file_tagger in self.file_taggers:
            tagger_result = file_tagger.run_tagger(file, **self.kwargs)
            file.tags.update(tagger_result)
            self.progress.update(self.task, advance=1)

        for doc_tagger in self.doc_taggers:
            if doc_tagger.dependencies:
                doc_tagger.import_tags(imported_tags)

            for doc_index, doc in enumerate(file.content):
                tagger_result = doc_tagger.run_tagger(doc, **self.kwargs)
                doc.tags.update(tagger_result)
                file.content[doc_index] = doc
                self.progress.update(self.task, advance=1)

        output_path = path.replace("documents", f"tags/{self.experiment}")

        self.file_client.write(output_path, file.get_tags())

    def get_total(self, paths: list[str], **kwargs) -> int:
        total = sum(
            [
                len(FileClient.get_for_target(path).read(path).splitlines())
                for path in paths
            ]
        )
        num_taggers = kwargs.get("num_taggers", 1)

        return total * num_taggers
