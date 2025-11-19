import sys
from pathlib import Path

if __name__ == "__main__":

    home = Path("/home/linus")
    template_file = home / "template.md"

    # read in template
    if not template_file.exists() or not template_file.is_file():
        sys.exit("Found no template file.")
    with template_file.open() as f:
        content = f.read()

    # official awesome repo: https://github.com/sindresorhus/awesome

    # check if at least the main title is present
    if "Requirements for your pull request" not in content:
        sys.exit("The template is incorrect.")

    # commit 2f7d2c7 (2f7d2c71e6d7e0db8b99288779f78945d8b6c2b4) contained typos,
    # which were later fixed in 8e71414 (8e71414aea13959f183b193f0bb62b1034c44fb4);
    # the sentence "It should not contain the name of the list." was added in 2f7d2c7;
    # we are using those differences to check weather the correct commit (2f7d2c7) was pulled.
    if "It should not contain the name of the list." not in content:
        sys.exit("This is not the template of the requested commit.")
    if "Your entry here should include a short description about the project/theme of the list." not in content:
        sys.exit("This is not the template of the requested commit.")

    # check that all checkboxes are marked as completed
    if "- [ ]" in content:
        sys.exit("Not all checkboxes are marked as completed.")

    sys.exit(0)
