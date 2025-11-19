import sys
from pathlib import Path

if __name__ == "__main__":

    home = Path("/home/linus")
    project_dir = home / "new_project"
    gitignore_file = project_dir / ".gitignore"

    if not gitignore_file.exists():
        sys.exit("Missing .gitignore file")

    with gitignore_file.open() as f:
        lines = list(line.strip() for line in f if line.strip() and not line.startswith("#"))

    # already included .gitignore entries that should be kept
    existing_entries = {
        "*.log",
        ".env",
        "output_data.csv",
    }

    # sample of expected additional .gitignore entries (official git repo)
    expected_entries = {
        "__pycache__/",
        ".Python",
        "build/",
        ".eggs/",
        "lib/",
        "lib64/",
        "var/",
        "wheels/",
        "pip-log.txt",
        ".cache",
        ".pytest_cache/",
        "local_settings.py",
        ".pybuilder/",
        ".ipynb_checkpoints",
        "env/",
        "venv/",
        "ENV/",
        ".pytype/",
    }

    # ensure expected patterns exist
    missing_entries = [e for e in (existing_entries | expected_entries) if e not in lines]
    if missing_entries:
        sys.exit("Missing expected entries in .gitignore")

    # ensure no duplicates
    if any(lines.count(e) > 1 for e in existing_entries):
        sys.exit(".gitignore contains duplicate entries")

    sys.exit(0)
