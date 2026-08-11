
from typing import List

from model.file import File
from model.filter import Filter

class FileSearchEngine:
    @staticmethod
    def search(files: List[File], filter: Filter) -> List[File]:
        return [file for file in files if filter.apply(file)]