from model.file import File
from model.filter import Filter, ExtensionFilter, SizeFilter, NameFilter
from service.file_search_engine import FileSearchEngine

def main():
    # Example usage of the File class

    files = []
    files.append(File(name="example.txt", size=10 * 1024, extension="txt")) # 10KB
    files.append(File(name="image.png", size=2 * 1024 * 1024, extension="png")) # 2MB
    files.append(File(name="Some Order.xml", size=2 * 1024, extension="xml")) # 2KB
    files.append(File(name="Purchase Order.png", size=2 * 1024, extension="png")) # 2KB
    files.append(File(name="my_folder", size=0, extension="", is_directory=True))

    # Testing the ExtensionFilter
    extension_filter = ExtensionFilter(extension="png")
    result = FileSearchEngine.search(files, extension_filter)
    print(f"Files with .png extension: {len(result)}")
    for file in result:
        print(file)

    # Testing the SizeFilter
    size_filter = SizeFilter(min_size=10 * 1024, max_size=5 * 1024 * 1024)
    result = FileSearchEngine.search(files, size_filter)
    print(f"\nFiles with size between 10KB and 5MB: {len(result)}")
    for file in result:
        print(file)

    # Testing the NameFilter
    name_filter = NameFilter(name="order")
    result = FileSearchEngine.search(files, name_filter)
    print(f"\nFiles with 'order' in the name: {len(result)}")
    for file in result:
        print(file)

    # Testing combined filters using logical operators
    combined_filter = (extension_filter & size_filter | name_filter)
    result = FileSearchEngine.search(files, combined_filter)
    print(f"\nFiles matching combined filter: {len(result)}")
    for file in result:
        print(file)

if __name__ == "__main__":
    main()