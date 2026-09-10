class File:
    def __init__(self, name: str, size: int, extension: str, is_directory: bool = False):
        self.name = name
        self.size = size
        self.extension = extension
        self.is_directory = is_directory

    def __repr__(self):
        return f"File(name={self.name}, size={self.size}, extension={self.extension}, is_directory={self.is_directory})"
