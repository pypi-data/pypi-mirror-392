import sys
from pathlib import Path

if __name__ == "__main__":

    home = Path("/home/linus")
    original_script = home / "lemon" / "tree" / "rand_n.py"
    copied_script = home / "rand_n.py"

    if not original_script.exists():
        sys.exit("Copy the script without moving the original.")
    if not copied_script.exists():
        sys.exit("There is no copy of the requested script.")

    if original_script.read_text() != copied_script.read_text():
        sys.exit("The script is not the same.")

    sys.exit(0)
