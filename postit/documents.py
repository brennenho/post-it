import json

from postit.files import FileClient
from postit.processor import BaseProcessor

# TODO: split each folder into multiple files after a certain size
# TODO: improve error handling
# TODO: improve logging and progress tracking


class DocumentGenerator(BaseProcessor):
    """
    Processor class for generating documents from files in a folder. Inherits from BaseProcessor.
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
        """
        Generates documents from files in the specified folder paths.
        """
        processor = DocumentGenerator(
            output_path=output_path,
            keep_raw=keep_raw,
            num_processes=num_processes,
        )
        processor.run(folder_paths)

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
        folder = file_client.glob(path)

        for id, file in enumerate(folder):
            if file_client.is_file(file):
                content = file_client.read(file)
                # Format document data in jsonl format
                file_data = {"id": id, "source": file, "content": content}
                folder_content += json.dumps(file_data) + "\n"

        # Get the top folder path to use as file name
        top_folder_path = get_top_folder(path)

        # Clean up the top folder
        if not self.keep_raw:
            file_client.remove(top_folder_path)

        # Write the folder content to a .jsonl file
        FileClient.get_for_target(self.output_path).write(
            f"{self.output_path}/{top_folder_path.split('/')[-1]}.jsonl", folder_content
        )


def get_top_folder(path: str) -> str:
    """
    Returns the top-level folder from the given path.

    Args:
        path (str): The path to extract the top-level folder from.

    Returns:
        str: The top-level folder path.
    """
    special_chars = ["*", "?", "[", "]", "{", "}"]  # Glob pattern special characters
    split_path = path.split("/")
    segments = []

    # Iterate over the path segments in reverse order
    for segment in reversed(split_path):
        if "**" in segment:
            continue

        # Check if the segment contains any special characters
        contains_special_chars = False
        for i, char in enumerate(segment):
            if char in special_chars:
                if i > 0 and segment[i - 1] == "/":
                    continue
                else:
                    contains_special_chars = True
                    break

        if not contains_special_chars:
            segments.append(segment)

    if not segments:
        return path

    # Join the segments in reverse order to get the top folder path
    top_folder_path = "/".join(reversed(segments))

    # Handle special cases for root and home directories
    if split_path[0] == "":
        return "/" + top_folder_path
    elif split_path[0] == "~":
        return "~/" + top_folder_path

    return top_folder_path
