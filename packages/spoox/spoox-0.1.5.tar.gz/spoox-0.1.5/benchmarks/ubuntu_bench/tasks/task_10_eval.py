import subprocess
import sys
import time
from pathlib import Path

if __name__ == "__main__":

    home = Path("/home/linus")

    try:
        start = time.time()
        result = subprocess.run("main -n pete -i 4", shell=True, capture_output=True, text=True, user='linus')
        end = time.time()

        if result.returncode != 0:
            sys.exit("Calling main failed.")

        if "pete-pete-pete-pete" not in result.stdout:
            sys.exit("Output of main wrong.")

        if end - start > 4:
            sys.exit("It took more than 4 seconds to execute.")

    except Exception as e:
        sys.exit("Calling main failed.")

    sys.exit(0)
