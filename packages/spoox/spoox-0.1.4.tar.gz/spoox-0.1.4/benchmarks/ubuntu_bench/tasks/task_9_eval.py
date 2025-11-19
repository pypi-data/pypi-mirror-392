import sys
from pathlib import Path
import requests

if __name__ == "__main__":

    home = Path("/home/linus")
    count_file = home / "jokes_count" / "count.md"

    # check if a result file exists
    if not count_file.exists() or not count_file.is_file():
        sys.exit("Can not find count file.")
    with count_file.open() as f:
        content = f.read()

    # get true number of jokes that contain the word "linux"
    response = requests.get("https://api.chucknorris.io/jokes/search?query=linux")
    if response.status_code == 200:
        joke_count = response.json().get("total", 0)
    else:
        sys.exit("Evaluation failed.")

    # check if count is correct
    if str(joke_count) not in content.replace('\n', ' ').split(' '):
        sys.exit("Number of matching jokes is wrong.")
