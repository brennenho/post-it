import json
import operator
import os
import yaml

from postit.files import FileClient
from postit.processor import BaseProcessor
from postit.utils.paths import get_documents_path
from typing import Union

# TODO: improve error handling


class Condition:
    """
    A condition to filter documents based on tags.

    Attributes:
        tag (str): The tag to filter on.

        operator (str): The operator to use for comparison.
            Supported operators: "in", "not in", "==", "!=", ">", "<", ">=", "<=".

        value (Union[float, str, list]): The value to compare against.
    """

    tag: str
    operator: str
    value: Union[float, str, list]

    def __init__(self, tag: str, operator: str, value: Union[float, str, list]):
        self.tag = tag
        self.operator = operator
        self.value = value

    @staticmethod
    def from_dict(data: dict) -> "Condition":
        return Condition(
            tag=data["tag"], operator=data["operator"], value=data["value"]
        )

    def eval(self, doc: dict) -> list:
        """
        Evaluate the given condition on the document and return a list of valid tags.

        Args:
            doc (dict): The document to evaluate the condition on.

        Returns:
            list: A list of valid tags that satisfy the condition.
        """
        operators = {
            "in": lambda x, y: x in y,
            "not in": lambda x, y: x not in y,
            "==": operator.eq,
            "!=": operator.ne,
            ">": operator.gt,
            "<": operator.lt,
            ">=": operator.ge,
            "<=": operator.le,
        }
        if self.operator not in operators:
            raise ValueError(f"Invalid operator: {self.operator}")

        return [
            tag
            for tag in doc.get(self.tag, [])
            if operators[self.operator](tag[2], self.value)
        ]


class MixerConfig:
    """
    Configuration for a mixer.

    Attributes:
        name (str): The name of the mixer.
        tags (list[str]): The tags associated with the mixer.
        input_paths (list[str]): The input paths for the mixer. Supports glob patterns.
        output_path (str): The output path for the mixer.
        conditions (dict[str, list[Condition]]): The conditions for the mixer.
    """

    name: str
    experiments: list[str]
    input_paths: list[str]
    output_path: str
    conditions: dict[str, list[Condition]]

    def __init__(
        self,
        name: str,
        experiments: list[str],
        input_paths: list[str],
        output_path: str = "",
        conditions: dict[str, list[Condition]] = {
            "include": [],
            "exclude": [],
        },
    ):
        self.name = name
        self.experiments = experiments
        self.input_paths = input_paths
        self.output_path = output_path
        self.conditions = conditions

    @staticmethod
    def load(path: str) -> "MixerConfig":
        """
        Create a MixerConfig object from a JSON or YAML file.
        """
        file_client = FileClient.get_for_target(path)
        if file_client.is_file(path):
            content = file_client.read(path)
            ext = os.path.splitext(path)[1]
            if ext == ".json":
                config = json.loads(content)
            elif ext in [".yml", ".yaml"]:
                config = yaml.safe_load(content)
            else:
                raise ValueError(f"Unsupported file format: {ext}")
        else:
            raise FileNotFoundError(f"File not found: {path}")

        conditions = {
            key: [Condition.from_dict(cond) for cond in value]
            for key, value in config["conditions"].items()
        }
        config["conditions"] = conditions

        return MixerConfig(**config)

    def save(self, path: str) -> None:
        """
        Write the MixerConfig object to a JSON or YAML file.
        """
        data = {
            "name": self.name,
            "experiments": self.experiments,
            "input_paths": self.input_paths,
            "output_path": self.output_path,
            "conditions": {
                key: [cond.__dict__ for cond in value]
                for key, value in self.conditions.items()
            },
        }
        ext = os.path.splitext(path)[1]
        if ext == ".json":
            content = json.dumps(data, indent=4)
        elif ext in [".yml", ".yaml"]:
            content = yaml.dump(data, indent=4)
        else:
            raise ValueError(f"Unsupported file format: {ext}")

        file_client = FileClient.get_for_target(path)
        file_client.write(path, content)


class Mixer(BaseProcessor):
    """
    Mix documents based on specified conditions.
    Use Mixer.mix() as the entry point.
    """

    label = "Mixing"

    @staticmethod
    def mix(config: MixerConfig, num_processes: int = 1) -> None:
        Mixer.label = f"Mixing ({config.name})"
        for input_path in config.input_paths:
            paths = [input_path]
            file_client = FileClient.get_for_target(input_path)
            if file_client.is_glob(input_path):
                paths = file_client.glob(input_path)
            processor = Mixer(
                file_client, config.experiments, config.conditions, num_processes
            )
            out_file = "".join(processor.run(paths, file_client=file_client))

            if not config.output_path:
                # Default output path is an adjacent directory with the mixer name
                mixer_directory = get_documents_path(input_path).replace(
                    "documents", config.name
                )
                config.output_path = f"{mixer_directory}/results.jsonl"

            file_client.write(config.output_path, out_file)

    def __init__(
        self,
        file_client: FileClient,
        experiments: list[str],
        conditions: dict[str, list[Condition]],
        num_processes: int = 1,
    ):
        super().__init__(num_processes)
        self.file_client = file_client
        self.experiments = experiments
        self.conditions = conditions

    def process(self, path: str) -> str:
        in_file = self.file_client.read(path).strip().split("\n")
        tags = []
        out_file = ""

        for exp in self.experiments:
            # Assume tags are in an adjacent directory
            # TODO: make this more flexible
            tag_path = path.replace("documents", f"tags/{exp}")
            tags.append(self.file_client.read(tag_path).strip().splitlines())

        # TODO: implement filtering by file tags
        file_tags = {}
        for tag in tags:
            file_tags.update(json.loads(tag[0])["tags"])

        for i in range(len(in_file)):
            doc: dict = json.loads(in_file[i])
            # Merge tags into document content
            doc_tags = self.merge_tags(
                doc["id"],
                [tag[i + 1] for tag in tags],  # Skip first line (file tags)
            )
            if doc_tags:
                doc.update(doc_tags)

            # Apply filtering to document content
            filtered_doc = self.apply_conditions(doc, self.conditions)

            # Remove empty documents
            if filtered_doc["content"]:
                out_file += json.dumps(filtered_doc) + "\n"

            self.progress.update(self.task, advance=1)

        return out_file

    def get_total(self, paths: list[str], **kwargs) -> int:
        file_client: FileClient = kwargs.get("file_client", None)
        return sum([len(file_client.read(path).splitlines()) for path in paths])

    def merge_tags(self, doc_id: str, raw_tags: list[str]) -> dict:
        tags = {}
        for tag in raw_tags:
            tag_json = json.loads(tag)
            if doc_id == tag_json["id"]:  # Check document ids match
                tags.update(tag_json["tags"])

        return tags

    def apply_conditions(
        self, doc: dict, conditions: dict[str, list[Condition]]
    ) -> dict:
        if not conditions:
            return doc

        include_conditions = conditions.get("include", [])
        exclude_conditions = conditions.get("exclude", [])

        include_results = [condition.eval(doc) for condition in include_conditions]
        exclude_results = [condition.eval(doc) for condition in exclude_conditions]

        # Merge include and exclude results
        merge = self.merge_ranges(include_results, exclude_results)

        filtered_content = "".join(
            [doc["content"][range[0] : range[1] + 1] for range in merge]
        )
        doc["content"] = filtered_content

        return doc

    def merge_ranges(
        self,
        include_ranges: list[list[list[int]]],
        exclude_ranges: list[list[list[int]]],
    ) -> list[list[int]]:
        def subtract_range(
            inc_range: list[int], exc_range: list[int]
        ) -> list[list[int]]:
            inc_start, inc_end, inc_value = inc_range
            exc_start, exc_end, _ = exc_range

            result: list[list[int]] = []
            if exc_end < inc_start or exc_start > inc_end:
                # Ranges do not overlap
                result.append(inc_range)
            else:
                # Ranges overlap
                if exc_start > inc_start:
                    result.append([inc_start, exc_start - 1, inc_value])
                if exc_end < inc_end:
                    result.append([exc_end + 1, inc_end, inc_value])

            return result

        def process_ranges(
            include_set: list[list[int]], exclude_set: list[list[int]]
        ) -> list[list[int]]:
            final_ranges = include_set[:]
            for exc_range in exclude_set:
                temp_ranges = []
                for inc_range in final_ranges:
                    temp_ranges.extend(subtract_range(inc_range, exc_range))
                final_ranges = temp_ranges
            return final_ranges

        final_result: list[list[int]] = []
        if not include_ranges:
            return final_result

        if not exclude_ranges:
            for include_set in include_ranges:
                final_result.extend(include_set)
            return final_result

        for include_set in include_ranges:
            for exclude_set in exclude_ranges:
                final_result.extend(process_ranges(include_set, exclude_set))

        return final_result
