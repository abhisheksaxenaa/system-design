from abc import ABC, abstractmethod
from typing import Optional

from model.file import File

class Filter(ABC):
    @abstractmethod
    def apply(self, file: File) -> bool:
        pass

    # Operator overloading for intuitive filter composition
    def __and__(self, other: "Filter") -> "Filter":
        return AndFilter(self, other)

    def __or__(self, other: "Filter") -> "Filter":
        return OrFilter(self, other)

    def __invert__(self) -> "Filter":
        return NotFilter(self)

class AndFilter(Filter):
    def __init__(self, *filters: Filter):
        self.filters = filters
    def apply(self, file: File) -> bool:
        return all(f.apply(file) for f in self.filters)

class OrFilter(Filter):
    def __init__(self, *filters: Filter):
        self.filters = filters

    def apply(self, file: File) -> bool:
        return any(f.apply(file) for f in self.filters)

class NotFilter(Filter):
    def __init__(self, filter: Filter):
        self.filter = filter

    def apply(self, file: File) -> bool:
        return not self.filter.apply(file)

class ExtensionFilter(Filter):
    def __init__(self, extension: str):
        self.extension = extension

    def apply(self, file: File) -> list:
        return file.extension == self.extension


class SizeFilter(Filter):
    def __init__(self, min_size: Optional[int], max_size: Optional[int]):
        self.min_size = min_size
        self.max_size = max_size

    def apply(self, file: File) -> list:
        if self.min_size is not None and file.size < self.min_size:
            return False
        if self.max_size is not None and file.size > self.max_size:
            return False
        return True

class NameFilter(Filter):
    def __init__(self, name: str, case_sensitive: bool = False):
        self.name = name
        self.case_sensitive = case_sensitive

    def apply(self, file: File) -> list:
        name = self.name
        file_name = file.name
        if not self.case_sensitive:
            name = name.lower()
            file_name = file_name.lower()
        return name in file_name