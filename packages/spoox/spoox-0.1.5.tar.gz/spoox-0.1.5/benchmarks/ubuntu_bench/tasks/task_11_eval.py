import subprocess
import sys

if __name__ == "__main__":

    # execute grep command and check if grep is case-insensitive by default
    result = subprocess.run(
        'echo "HELLO" | grep Hello',
        shell=True,
        capture_output=True,
        text=True,
        user='linus'
    )
    if 'hello' in result.stdout.lower():
        sys.exit(0)
    else:
        sys.exit("The grep command is still case sensitive.")

