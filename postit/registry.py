import os

from importlib.util import module_from_spec, spec_from_file_location
from postit.files import FileClient


class TaggerRegistry:
    """
    A singleton registry to store taggers and allow for loading of custom taggers.
    Register custom taggers by deriving from DocTagger or FileTagger and using the @tagger decorator.

    Example:
        .. code-block:: python

            @tagger
            class CustomTagger(DocTagger) -> TagResult:
                name = "custom_tagger"
                def predict(self, doc):
                    return TagResult(doc, [])
    """

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(TaggerRegistry, cls).__new__(cls)
            cls._instance._registry = {}
        return cls._instance

    @classmethod
    def add(cls):
        cls()  # Ensure the registry is initialized

        def decorator(func):
            name = ""
            # Use the name attribute if it exists, otherwise use the function name
            if hasattr(func, "name"):
                name = func.name
            else:
                name = func.__name__
            cls._instance._registry[name] = func
            return func

        return decorator

    @classmethod
    def get(cls, name):
        cls()  # Ensure the registry is initialized

        tagger = cls._instance._registry.get(name)
        if not tagger:
            raise ValueError(
                f"Unknown tagger: {name}. Available taggers: {[tagger for tagger in cls._instance._registry.keys()]}"
            )
        return tagger

    @classmethod
    def all(cls):
        cls()  # Ensure the registry is initialized

        return cls._instance._registry

    @classmethod
    def names(cls):
        cls()  # Ensure the registry is initialized

        return list(cls._instance._registry.keys())

    @staticmethod
    def import_modules(file_paths: list[str]):
        """
        Import tagger modules from the specified file paths.

        Args:
            file_paths (list[str]): A list of file paths to import tagger modules from. Glob patterns are supported.

        Raises:
            ImportError: If a module cannot be imported from a file path.
        """
        for file_path in file_paths:
            paths = [file_path]
            # If the file path is a directory, expand any glob patterns
            if not os.path.isfile(file_path):
                paths = FileClient().glob(file_path)

            # Import each module from the file paths
            for path in paths:
                module_name = os.path.splitext(os.path.basename(path))[0]
                spec = spec_from_file_location(module_name, path)
                if spec is None or spec.loader is None:
                    raise ImportError(f"Can't import {module_name} from {path}")
                module = module_from_spec(spec)
                spec.loader.exec_module(module)


def tagger(cls):
    """
    A utility decorator function that adds the decorated class to the TaggerRegistry.
    Use @tagger on a class derived from DocTagger or FileTagger to add it to the registry.

    Taggers are added to the registry using the `name` attribute of the class if it exists.
    Will default to the class name if the `name` attribute is not present.
    """
    return TaggerRegistry.add()(cls)


# Import default taggers
TaggerRegistry.import_modules(["postit/taggers/**/*.py"])
