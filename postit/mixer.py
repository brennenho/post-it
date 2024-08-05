import json
import operator

from postit.files import FileClient
from postit.processor import BaseProcessor
from postit.utils import get_documents_path
from typing import Union

# TODO: improve error handling
# TODO: improve logging and progress tracking


class Condition:
    """
    Represents a condition for filtering data.

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

        valid_tags = []
        for tag in doc.get(self.tag, []):
            if operators[self.operator](tag[2], self.value):
                valid_tags.append(tag)

        return valid_tags


class MixerConfig:
    """
    Represents the configuration for a mixer.

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


class Mixer(BaseProcessor):
    label = "Mixing"

    @staticmethod
    def mix(config: MixerConfig, num_processes: int = 1) -> None:
        for input_path in config.input_paths:
            paths = [input_path]
            file_client = FileClient.get_for_target(input_path)
            if file_client.is_glob(input_path):
                paths = file_client.glob(input_path)
            processor = Mixer(
                file_client, config.experiments, config.conditions, num_processes
            )
            out_file = "".join(processor.run(paths))

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

        return out_file

    def merge_tags(self, doc_id: str, raw_tags: list[str]) -> dict:
        """
        Merges tags from a list of raw tags based on the document index.

        Args:
            doc_id (str): The id of the document.
            raw_tags (list[str]): A list of raw tags in JSON format.

        Returns:
            dict: A dictionary containing the merged tags.

        """
        tags = {}
        for tag in raw_tags:
            tag_json = json.loads(tag)
            if doc_id == tag_json["id"]:  # Check document ids match
                tags.update(tag_json["tags"])

        return tags

    def apply_conditions(
        self, doc: dict, conditions: dict[str, list[Condition]]
    ) -> dict:
        """
        Apply conditions to filter the content of a document.

        Args:
            doc (dict): The document to be filtered.
            conditions (dict[str, list[Condition]]): The conditions to be applied.

        Returns:
            dict: The filtered document.

        Raises:
            ValueError: If an invalid operator is used in the conditions.
        """
        if not conditions:
            return doc

        include_conditions = conditions.get("include", [])
        exclude_conditions = conditions.get("exclude", [])

        include_results = [condition.eval(doc) for condition in include_conditions]
        exclude_results = [condition.eval(doc) for condition in exclude_conditions]

        # Merge include and exclude results
        merge = self.merge_ranges(include_results, exclude_results)
        filtered_content = ""
        for range in merge:
            # Use merged ranges to filter content
            filtered_content += doc["content"][range[0] : range[1] + 1]

        doc["content"] = filtered_content
        return doc

    def merge_ranges(
        self,
        include_ranges: list[list[list[int]]],
        exclude_ranges: list[list[list[int]]],
    ) -> list[list[int]]:
        """
        Merge the include_ranges and exclude_ranges to generate the final result.

        Args:
            include_ranges (list[list[list[int]]]): A list of include ranges.
            exclude_ranges (list[list[list[int]]]): A list of exclude ranges.

        Returns:
            list[list[int]]: The final result after processing the ranges.
        """

        def subtract_range(
            inc_range: list[int], exc_range: list[int]
        ) -> list[list[int]]:
            """
            Subtract the excluded range from the included range.

            Args:
                inc_range (list[int]): The included range represented as a list of three integers: [start, end, value].
                exc_range (list[int]): The excluded range represented as a list of three integers: [start, end, value].

            Returns:
                list[list[int]]: A list of ranges resulting from subtracting the excluded range from the included range.
            """
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
            """
            Process the given include and exclude sets of ranges and return the final ranges.

            Args:
                include_set (list[list[int]]): A list of inclusive ranges.
                exclude_set (list[list[int]]): A list of exclusive ranges.

            Returns:
                list[list[int]]: The final ranges after processing the include and exclude sets.
            """
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
