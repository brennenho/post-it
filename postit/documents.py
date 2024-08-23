import json

from postit.files import FileClient
from postit.processor import BaseProcessor
from postit.utils.paths import get_top_folder

# TODO: split each folder into multiple files after a certain size
# TODO: improve error handling


class DocumentGenerator(BaseProcessor):
    """
    Generates documents from files in the specified folder paths.
    One folder is processed per thread at a time.

    Use DocumentGenerator.generate() as the entry point.
    """

    label = "Generating Documents"

    @staticmethod
    def generate(
        folder_paths: list[str],
        output_path: str = "./documents",
        keep_raw: bool = True,
        num_processes: int = 1,
    ):
        processor = DocumentGenerator(
            output_path=output_path,
            keep_raw=keep_raw,
            num_processes=num_processes,
        )

        subfolders = []
        for path in folder_paths:
            file_client = FileClient.get_for_target(path)
            subfolders.extend(file_client.glob(path))
        processor.run(subfolders)

    def __init__(
        self,
        output_path: str = "./documents",
        keep_raw: bool = True,
        num_processes: int = 1,
    ):
        super().__init__(num_processes)
        self.output_path = output_path
        self.keep_raw = keep_raw

    def process(self, path: str):
        """
        Processes a folder by reading the files and writing the content to a .jsonl file.
        """
        folder_content = ""
        file_client = FileClient.get_for_target(path)
        folder = file_client.glob(f"{path}/**/*")

        for id, file in enumerate(folder):
            if file_client.is_file(file):
                content = file_client.read(file)
                # Format document data in jsonl format
                file_data = {"id": id, "source": file, "content": content}
                folder_content += json.dumps(file_data) + "\n"
                self.progress.update(self.task, advance=1)

        # Get the top folder path to use as file name
        top_folder_path = get_top_folder(path)

        # Clean up the top folder
        if not self.keep_raw:
            file_client.remove(top_folder_path)

        # Write the folder content to a .jsonl file
        FileClient.get_for_target(self.output_path).write(
            f"{self.output_path}/{top_folder_path.split('/')[-1]}.jsonl", folder_content
        )

    def get_total(self, paths: list[str], **kwargs) -> int:
        total = 0
        for path in paths:
            file_client = FileClient.get_for_target(path)
            total += sum(
                [
                    file_client.get_file_count(f"{g}/**/*")
                    for g in file_client.glob(path)
                ]
            )

        return total
