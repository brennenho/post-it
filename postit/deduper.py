from postit.files import FileClient
from postit.processor import TaggerProcessor
from postit.utils.bloom import BloomFilter
from postit.utils.logging import get_logger
from postit.utils.paths import get_ext
from typing import Any

logger = get_logger(__name__)


class Deduper(TaggerProcessor):
    """
    Uses tagging framework to tag documents as duplicates.
    Use Deduper.dedupe() as the entry point.
    """

    label = "Deduplicating"

    @staticmethod
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
        """
        Deduplicate documents using taggers.

        Args:
            glob_paths (list[str]): List of glob patterns for the documents to deduplicate.
            experiment (str): Name of the experiment. Defaults to "dedupe".
            dedupe_docs (bool, optional): Toggle to deduplicate at the document level. Defaults to False.
            dedupe_paragraphs (bool, optional): Whether to deduplicate at the paragraph level. Defaults to False.
            bloom_size (int, optional): Size of the bloom filter. Defaults to 1000000.
            bloom_file (str, optional): Path to a bloom filter file to import.
            num_processes (int, optional): Number of processes to use for parallel processing. Defaults to 1.
        """
        Deduper.label = f"Deduping ({experiment})"
        tagger_names = []
        if dedupe_docs:
            tagger_names.append("doc_dedupe")
        if dedupe_paragraphs:
            tagger_names.append("paragraph_dedupe")

        bloom = None
        if bloom_file:
            if get_ext(bloom_file) != ".pkl":
                raise ValueError("Bloom filter file must be a pickle file. (.pkl)")
            file_client = FileClient.get_for_target(bloom_file)
            if file_client.is_file(bloom_file):
                bloom = BloomFilter.load(bloom_file)
                logger.info(f"Succesfully loaded bloom filter: {bloom_file}.")
            else:
                logger.warning(
                    f"Cannot load bloom filter: {bloom_file}. Creating a new bloom filter."
                )

        if not bloom:
            bloom = BloomFilter.new(bloom_size, 0.01)

        for glob_path in glob_paths:
            file_client = FileClient.get_for_target(glob_path)
            document_paths = file_client.glob(glob_path)
            processor = Deduper(
                tagger_names=tagger_names,
                experiment=experiment,
                file_client=file_client,
                num_processes=num_processes,
                bloom=bloom,
                **kwargs,
            )
            processor.run(
                document_paths, file_client=file_client, num_taggers=len(tagger_names)
            )

        if bloom_file:
            bloom.save(bloom_file)

    def get_total(self, paths: list[str], **kwargs) -> int:
        file_client: FileClient = kwargs.get("file_client", None)
        num_taggers = kwargs.get("num_taggers", 1)
        total = sum([len(file_client.read(path).splitlines()) for path in paths])
        return total * num_taggers
