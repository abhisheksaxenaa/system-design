# System Requirements

Design a linux style find file

## Functional Requirements

- The system should be able find files by name
- The system should be able to find files by size e.g., greater than 5 MB, less than 5 MB
- The system should be able to find files by extension
- The system should be extensible for any new filter

## Entities

File
    |- Name
    |- Size
    |- Extension

Filter (abstract)
    |= apply - # Apply the logic
    |= __and__ # operator overloading multiple filters
    |= __or__ # operator overloading multiple filters

FileSearchEnginer
    |- search
