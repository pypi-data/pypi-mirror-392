import argparse
import shutil
import os
import subprocess


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
    
    # Delete main.py if it exists in root
    main_py_path = os.path.join(current_dir, "main.py")
    if os.path.exists(main_py_path):
        os.remove(main_py_path)
        print("Removed existing main.py")
    
    # Files to overwrite if they exist
    overwrite_files = {".gitignore", "uv.lock", "pyproject.toml"}
    
    for entry in os.scandir(template_dir):
        item = entry.name
        src = entry.path
        dst = os.path.join(current_dir, item)
        should_copy = True
        if os.path.exists(dst):
            if item in overwrite_files:
                # Overwrite
                if entry.is_dir():
                    shutil.rmtree(dst)
                    shutil.copytree(src, dst)
                else:
                    shutil.copy2(src, dst)
                print(f"Copied {item} (overwritten)")
                should_copy = False  # Already copied
            else:
                print(f"Skipping {item}: already exists")
                should_copy = False
        if should_copy:
            if entry.is_dir():
                shutil.copytree(src, dst)
            else:
                shutil.copy2(src, dst)
            print(f"Copied {item}")

    # Replace ___APPLICATION_NAME___ with the provided name in all copied files
    replace_in_files(current_dir, "___APPLICATION_NAME___", name)

    print(f"FastAppear project '{name}' initialized!")

    # Run uv sync to install dependencies
    try:
        subprocess.run(["uv", "sync"], cwd=current_dir, check=True)
        print("Dependencies installed with uv sync.")
    except subprocess.CalledProcessError:
        print("Warning: Failed to run 'uv sync'. Please run it manually to install dependencies.")
    except FileNotFoundError:
        print("Warning: 'uv' command not found. Please install uv and run 'uv sync' to install dependencies.")


def replace_in_files(directory: str, old: str, new: str) -> None:
    """Recursively replace text in all files in the directory."""
    for root, dirs, files in os.walk(directory):
        # Skip directories we don't want to modify
        dirs[:] = [d for d in dirs if d not in {'.venv', '__pycache__', '.git'} and 'site-packages' not in root]
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
