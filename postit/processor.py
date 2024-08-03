from postit.files import FileClient
from postit.registry import TaggerRegistry
from postit.tagging import DocTagger, FileTagger
from postit.types import File

# IN PROGRESS
# TODO: implement as a class
# TODO: implement parallel processing
# TODO: improve error handling
# TODO: improve logging and progress tracking


def process(
    glob_paths: list[str],
    tagger_names: list[str],
    experiment: str,
    imported_experiments: list[str] = [],
) -> None:
    taggers = [TaggerRegistry.get(tagger)() for tagger in tagger_names]
    doc_taggers: list[DocTagger] = []
    file_taggers: list[FileTagger] = []

    for tagger in taggers:
        if isinstance(tagger, DocTagger):
            doc_taggers.append(tagger)
        elif isinstance(tagger, FileTagger):
            file_taggers.append(tagger)
        else:
            raise ValueError(f"Unknown tagger type: {tagger}")

    for glob_path in glob_paths:
        file_client = FileClient.get_for_target(glob_path)
        document_paths = file_client.glob(glob_path)

        for path in document_paths:
            file = File.from_raw(path, file_client.read(path))
            imported_tags = []
            for imported_experiment in imported_experiments:
                imported_tags.append(
                    file_client.read(
                        path.replace("documents", f"tags/{imported_experiment}")
                    )
                    .strip()
                    .splitlines()
                )

            for file_tagger in file_taggers:
                tagger_result = file_tagger.run_tagger(file, experiment)
                file.tags.update(tagger_result)

            for doc_tagger in doc_taggers:
                if doc_tagger.dependencies:
                    doc_tagger.import_tags(imported_tags)
                for doc_index, doc in enumerate(file.content):
                    tagger_result = doc_tagger.run_tagger(doc, experiment)
                    doc.tags.update(tagger_result)
                    file.content[doc_index] = doc

            output_path = path.replace("documents", f"tags/{experiment}")

            file_client.write(output_path, file.get_tags())
