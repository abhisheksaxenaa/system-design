# File Find System

A simple Linux-style file search system built with a filter abstraction that supports name, size, and extension matching.

## Overview

This implementation models files and search filters as separate objects. The search engine applies a composed filter to a list of file objects and returns matching results.

The design focuses on:
- clear separation of responsibilities
- reusable filter composition
- easy extensibility for new filter types

## Project Structure

- `main.py` - example usage and test cases
- `model/file.py` - `File` entity
- `model/filter.py` - abstract `Filter` base class, boolean filter operators, and concrete filters
- `model/extension_filter.py` - not used in the current package layout (filters are defined in `model/filter.py`)
- `service/file_search_engine.py` - `FileSearchEngine.search()` implementation

## Key Components

### File

`model/file.py` defines the `File` class with:
- `name` - the file name
- `size` - the file size in bytes
- `extension` - the file extension
- `is_directory` - boolean flag for directories

Example:
```python
File(name="example.txt", size=10 * 1024, extension="txt")
```

### Filter abstraction

`model/filter.py` defines an abstract `Filter` base class with a single method:
- `apply(file: File) -> bool`

Concrete filters implement this method to decide whether a file matches a condition.

The base class also supports filter composition using operator overloading:
- `&` => `AndFilter`
- `|` => `OrFilter`
- `~` => `NotFilter`

This makes it possible to build complex queries such as:
```python
combined_filter = (extension_filter & size_filter & ~exclude_name_filter) | name_filter
```

### Concrete filters

Implemented filters:
- `ExtensionFilter` - matches a file extension
- `SizeFilter` - matches files inside an optional min/max size range
- `NameFilter` - matches files whose name contains a string (case-insensitive by default)

### Search engine

`service/file_search_engine.py` provides:
- `FileSearchEngine.search(files, filter)`

It iterates through the given files and returns files for which `filter.apply(file)` is `True`.

## Example Usage

`main.py` demonstrates:
- creating sample `File` objects
- searching by extension
- searching by size range
- searching by name substring
- combining filters with `&`, `|`, and `~`

## Extensibility

To add a new filter:
1. create a new class inheriting from `Filter`
2. implement `apply(self, file: File) -> bool`
3. use the new filter in `FileSearchEngine.search()` or compose it with existing filters

Example:
```python
class ModifiedDateFilter(Filter):
    def __init__(self, earliest_timestamp):
        self.earliest_timestamp = earliest_timestamp

    def apply(self, file: File) -> bool:
        return file.modified_at >= self.earliest_timestamp
```

## Notes

- `model/extension_filter.py` is present but the active filter classes are defined in `model/filter.py`.
- The current design is a simple in-memory search engine; the engine can be extended to traverse actual file system paths and create `File` objects dynamically.
