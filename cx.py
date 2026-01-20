import os

def print_tree(start_path, prefix=""):
    """Recursively prints a directory tree structure."""
    try:
        items = os.listdir(start_path)
    except PermissionError:
        print(f"{prefix}[Permission Denied]")
        return

    for index, item in enumerate(sorted(items)):
        path = os.path.join(start_path, item)
        connector = "└── " if index == len(items) - 1 else "├── "
        print(prefix + connector + item)
        if os.path.isdir(path):
            extension = "    " if index == len(items) - 1 else "│   "
            print_tree(path, prefix + extension)

if __name__ == "__main__":
    folder = input("Enter folder path: ").strip()
    if os.path.exists(folder):
        print(folder)
        print_tree(folder)
    else:
        print("Invalid path.")