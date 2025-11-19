import sys
from pathlib import Path

if __name__ == "__main__":

    src_dir = Path("/home/linus/src")
    hello_file = src_dir / "hello_world.txt"

    if not hello_file.exists():
        sys.exit("hello_world.txt not found")

    hello_file_text = hello_file.read_text().lower()
    if "hello world" not in hello_file_text and "hello, world" not in hello_file_text:
        sys.exit("hello_world.txt content is wrong")

    sys.exit(0)
