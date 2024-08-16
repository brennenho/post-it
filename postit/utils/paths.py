import os


def get_documents_path(path: str) -> str:
    segments = path.split(os.sep)

    try:
        seg_idx = segments.index("documents")
    except ValueError:
        raise ValueError("No `documents` directory found in the path.")

    return os.sep.join(segments[: seg_idx + 1])


def get_ext(path: str) -> str:
    return os.path.splitext(path)[1]


def get_top_folder(path: str) -> str:
    special_chars = ["*", "?", "[", "]", "{", "}"]  # Glob pattern special characters
    split_path = path.split("/")
    segments = []

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

    top_folder_path = "/".join(reversed(segments))

    # Handle special cases for root and home directories
    if split_path[0] == "":
        return "/" + top_folder_path
    elif split_path[0] == "~":
        return "~/" + top_folder_path

    return top_folder_path
