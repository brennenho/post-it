import json

from postit.files import FileClient

# TODO: split each folder into multiple files after a certain size
def generate_documents(folder_paths: list[str], output_path: str = "./documents", keep_raw: bool = True) -> None:
    expanded_folders: list[str] = [FileClient.get_for_target(path).glob(path) for path in folder_paths]

    for folder_index, folder in enumerate(expanded_folders):
        folder_content = ""
        file_client = FileClient.get_for_target(folder_paths[folder_index])

        for idx, file in enumerate(folder):
            content = file_client.read(file)
            file_data = {"idx": idx, "source": file, "content": content}
            folder_content += json.dumps(file_data) + "\n"

        top_folder_path = get_top_folder(folder_paths[folder_index])

        if not keep_raw:
            file_client.remove(top_folder_path)

        FileClient.get_for_target(output_path).write(f"{output_path}/{top_folder_path.split('/')[-1]}.jsonl", folder_content)
        
def get_top_folder(path: str) -> str:
    special_chars = ["*", "?", "[", "]", "{", "}"]
    split_path = path.split("/")
    segments = []

    for segment in reversed(split_path):
        if "**" in segment:
            continue

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
    
    top_folder_path = "/".join(reversed(segments))

    if split_path[0] == "":
        return "/" + top_folder_path
    elif split_path[0] == "~":
        return "~/" + top_folder_path
    
    return top_folder_path
