import subprocess
import sys
from pathlib import Path
from typing import Tuple


def run_command(command: str) -> Tuple[int, str, str]:
    result = subprocess.run(
        command, shell=True,
        stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, user='linus'
    )
    return result.returncode, result.stdout.strip(), result.stderr.strip()


if __name__ == "__main__":

    home = Path("/home/linus")
    wordcount_script = home / "scripts" / "wordcount.sh"
    correct_wordcount_script = Path("/opt/wordcount.sh")
    dummy_text = Path("/opt/sample.txt")

    # check if script exists
    if not wordcount_script.is_file():
        sys.exit("Script wordcount.sh is missing.")

    # run scripts and compare output - test 1
    code, out, err = run_command(f"{wordcount_script} {dummy_text} 4")
    code_e, out_e, err_e = run_command(f"{correct_wordcount_script} {dummy_text} 4")
    print(code, out, err)
    print(code_e, out_e, err_e)
    if not code == code_e or not out == out_e or not err == err_e:
        sys.exit("Output of script not as expected.")

    # run scripts and compare output - test 2
    code, out, err = run_command(f"{wordcount_script} {dummy_text} -4")
    code_e, out_e, err_e = run_command(f"{correct_wordcount_script} {dummy_text} -4")
    print(code, out, err)
    print(code_e, out_e, err_e)
    if not code == code_e or not out == out_e or not err == err_e:
        sys.exit("Output of script not as expected.")

    sys.exit(0)
