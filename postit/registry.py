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
    def add(cls, name=None):
        """
        Decorator to add a tagger function to the registry.

        Args:
            name (str, optional): The name of the tagger. If not provided, the function name will be used.

        Returns:
            The decorated function.
        """
        cls()  # Ensure the registry is initialized

        def decorator(func):
            nonlocal name
            if name is None:
                name = func.__name__
            cls._instance._registry[name] = func
            return func

        return decorator

    @classmethod
    def get(cls, name):
        """
        Get a tagger function from the registry.

        Args:
            name (str): The name of the tagger.

        Returns:
            The tagger function.

        Raises:
            ValueError: If the specified tagger name is not found in the registry.
        """
        tagger = cls._instance._registry.get(name)
        if not tagger:
            raise ValueError(
                f"Unknown tagger: {name}. Available taggers: {[tagger for tagger in cls._instance._registry.keys()]}"
            )
        return tagger

    @classmethod
    def all(cls):
        """
        Get all tagger functions from the registry.

        Returns:
            A dictionary containing all tagger functions, where the keys are the tagger names and the values are the functions.
        """
        return cls._instance._registry

    @classmethod
    def import_modules(cls, file_paths: list[str]):
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

    Taggers are added to the registry using the class name as the tagger name.
    """
    return TaggerRegistry.add()(cls)


# Import default taggers
TaggerRegistry.import_modules(["postit/taggers/*.py"])
