import sys
from pathlib import Path

if __name__ == "__main__":

    home = Path("/home/linus")
    sol_file = home / "jp_mail.txt"

    # check 'jp_mail' solution file and validate content
    if not sol_file.is_file():
        sys.exit("Missing jp_mail.txt")
    with sol_file.open() as f:
        content = f.read()
        if "pete@johnmail.com" not in content.lower():
            sys.exit("Incorrect mail address")
