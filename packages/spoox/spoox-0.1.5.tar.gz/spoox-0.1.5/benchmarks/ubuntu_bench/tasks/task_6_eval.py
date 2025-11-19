import subprocess
import sys
from pathlib import Path
import json

if __name__ == "__main__":

    home = Path("/home/linus")
    response_file = home / "response.json"

    # check if httpie can be executed and is installed in venv
    try:
        result = subprocess.run("/home/linus/virtuals/net_venv/bin/http https://jsonplaceholder.typicode.com/todos/4 --json", shell=True, capture_output=True, text=True, user='linus')
        if result.returncode != 0:
            sys.exit("Using http did not work.")
    except Exception as e:
        sys.exit("Using http did not work.")

    # check fetched data
    if not response_file.exists() or not response_file.is_file():
        sys.exit("Missing response.json file")
    try:
        with response_file.open() as f:
            data = json.load(f)
        if data.get("userId") != 1 or data.get("id") != 4 or data.get("title") != "et porro tempora":
            sys.exit("response.json is incorrect")
    except Exception as e:
        sys.exit("response.json is incorrect")

    sys.exit(0)
