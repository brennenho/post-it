import json

from postit.files import FileClient


# TODO: split each folder into multiple files after a certain size
def generate_documents(
    folder_paths: list[str], output_path: str = "./documents", keep_raw: bool = True
) -> None:
    """
    Generate structured documents in JSONL format from a list of folder paths.

    Args:
        folder_paths (list[str]): A list of folder paths containing the files to generate documents from.
            Glob patterns are supported.

        output_path (str, optional): The output path where the generated documents will be saved.
            Defaults to "./documents". Output path must be a directory named "documents".

        keep_raw (bool, optional): Toggle to keep the raw files after generating documents. Defaults to True.
    """

    # Expand any glob patterns
    expanded_folders: list[list[str]] = [
        FileClient.get_for_target(path).glob(path) for path in folder_paths
    ]

    for folder_index, folder in enumerate(expanded_folders):
        folder_content = ""
        # Initialize a new FileClient for each folder to allow mixing local and remote paths
        file_client = FileClient.get_for_target(folder_paths[folder_index])

        for idx, file in enumerate(folder):
            content = file_client.read(file)
            # Format document data in jsonl format
            file_data = {"idx": idx, "source": file, "content": content}
            folder_content += json.dumps(file_data) + "\n"

        # Get the top folder path to use as file name
        top_folder_path = get_top_folder(folder_paths[folder_index])

        # Clean up the top folder
        if not keep_raw:
            file_client.remove(top_folder_path)

        # Write the folder content to a .jsonl file
        FileClient.get_for_target(output_path).write(
            f"{output_path}/{top_folder_path.split('/')[-1]}.jsonl", folder_content
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
        for idx, char in enumerate(segment):
            if char in special_chars:
                if idx > 0 and segment[idx - 1] == "/":
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
