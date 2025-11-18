import argparse
import shutil
import os


def main() -> None:
    parser = argparse.ArgumentParser(description="FastAppear - FastAPI project scaffolding")
    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Subcommand for init
    init_parser = subparsers.add_parser("init", help="Initialize a new FastAppear project")
    init_parser.add_argument("name", help="Name of the application")

    # If no subcommand, show help
    args = parser.parse_args()

    if args.command == "init":
        init_project(args.name)
    else:
        parser.print_help()


def init_project(name: str) -> None:
    """Initialize a new FastAppear project by copying template files."""
    template_dir = os.path.join(os.path.dirname(__file__), "template")
    if not os.path.exists(template_dir):
        print("Error: Template directory not found in package.")
        return

    current_dir = os.getcwd()
    for entry in os.scandir(template_dir):
        item = entry.name
        src = entry.path
        dst = os.path.join(current_dir, item)
        if os.path.exists(dst):
            print(f"Skipping {item}: already exists")
        else:
            if entry.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"Copied {item}")

    # Replace ___APPLICATION_NAME___ with the provided name in all copied files
    replace_in_files(current_dir, "___APPLICATION_NAME___", name)

    print(f"FastAppear project '{name}' initialized!")


def replace_in_files(directory: str, old: str, new: str) -> None:
    """Recursively replace text in all files in the directory."""
    for root, dirs, files in os.walk(directory):
        for file in files:
            filepath = os.path.join(root, file)
            try:
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                if old in content:
                    content = content.replace(old, new)
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(content)
                    print(f"Updated {filepath}")
            except (UnicodeDecodeError, OSError):
                # Skip binary files or unreadable files
                pass


if __name__ == "__main__":
    main()
