import os


def get_documents_path(path: str) -> str:
    """
    Returns the path to the documents directory from the given path.

    Args:
        path (str): The path to extract the documents directory from.

    Returns:
        str: The path to the documents directory.
    """
    segments = path.split(os.sep)

    try:
        seg_idx = segments.index("documents")
    except ValueError:
        raise ValueError("No `documents` directory found in the path.")

    return os.sep.join(segments[: seg_idx + 1])


def get_ext(path: str) -> str:
    """
    Returns the file extension of the given path.

    Args:
        path (str): The path to extract the file extension from.

    Returns:
        str: The file extension.
    """
    return os.path.splitext(path)[1]
