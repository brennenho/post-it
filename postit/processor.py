import concurrent.futures

from concurrent.futures import ThreadPoolExecutor
from postit.files import FileClient
from postit.logging import get_logger
from postit.registry import TaggerRegistry
from postit.tagging import DocTagger, FileTagger
from postit.types import File
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    SpinnerColumn,
    TaskProgressColumn,
    TextColumn,
)

# IN PROGRESS
# TODO: implement as a class
# TODO: implement parallel processing
# TODO: improve error handling
# TODO: improve logging and progress tracking

logger = get_logger(__name__)


class BaseProcessor:
    """
    Abstract base class for processing files in parallel.

    Args:
        num_processes (int): Number of processes to run in parallel.

    Methods:
        process: Abstract method to be implemented by subclasses.
        run: Runs the processing on multiple paths in parallel using ThreadPoolExecutor.
    """

    label: str = "Processing"

    def __init__(self, num_processes: int = 1):
        self.num_processes = num_processes
        self.progress = Progress(
            TextColumn("[progress.description]{task.description}"),
            SpinnerColumn(),
            BarColumn(),
            TaskProgressColumn(),
            MofNCompleteColumn(),
        )

    def process(self, *args, **kwargs):
        """
        Abstract method to process a single file. Implemented by subclasses.
        """
        raise NotImplementedError

    def process_with_progress(self, *args, **kwargs):
        result = self.process(*args, **kwargs)
        self.progress.update(self.task, advance=1)
        return result

    def run(self, paths: list[str]):
        """
        Runs the processing on multiple paths in parallel using ThreadPoolExecutor.
        """
        logger.info(
            f"{self.label} {len(paths)} files using {self.num_processes} processes."
        )
        with self.progress:
            self.task = self.progress.add_task(
                f"[yellow]{self.label}", total=len(paths)
            )
            with ThreadPoolExecutor(max_workers=self.num_processes) as executor:
                futures = {
                    executor.submit(self.process_with_progress, path): path
                    for path in paths
                }

                results = []
                for future in concurrent.futures.as_completed(futures):
                    results.append(future.result())

                self.progress.update(
                    self.task,
                    description=f"[green]:heavy_check_mark: {self.label}",
                )
                return results


class TaggerProcessor(BaseProcessor):
    """
    Processor class for tagging documents using taggers. Inherits from BaseProcessor.
    One file is processed per thread at a time.

    Use TaggerProcessor.tag() as the entry point.
    """

    label = "Tagging"

    @staticmethod
    def tag(
        glob_paths: list[str],
        tagger_names: list[str],
        experiment: str,
        imported_experiments: list[str] = [],
        num_processes: int = 1,
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
        for glob_path in glob_paths:
            file_client = FileClient.get_for_target(glob_path)
            document_paths = file_client.glob(glob_path)
            processor = TaggerProcessor(
                tagger_names=tagger_names,
                experiment=experiment,
                file_client=file_client,
                imported_experiments=imported_experiments,
                num_processes=num_processes,
            )
            processor.run(document_paths)

    def __init__(
        self,
        tagger_names: list[str],
        experiment: str,
        file_client: FileClient,
        imported_experiments: list[str] = [],
        num_processes: int = 1,
    ):
        super().__init__(num_processes)
        self.experiment = experiment
        self.file_client = file_client
        self.imported_experiments = imported_experiments
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
        """
        Tag a single file using the specified taggers.

        Args:
            path (str): The path of the file to be processed.
        """

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
            tagger_result = file_tagger.run_tagger(file, self.experiment)
            file.tags.update(tagger_result)

        for doc_tagger in self.doc_taggers:
            if doc_tagger.dependencies:
                doc_tagger.import_tags(imported_tags)
            for doc_index, doc in enumerate(file.content):
                tagger_result = doc_tagger.run_tagger(doc, self.experiment)
                doc.tags.update(tagger_result)
                file.content[doc_index] = doc

        output_path = path.replace("documents", f"tags/{self.experiment}")

        self.file_client.write(output_path, file.get_tags())
