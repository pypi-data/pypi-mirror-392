import os
import subprocess
import sys

if __name__ == "__main__":

    # attention: this file must work when executed with python 2.7 and python 3.x
    game_file = os.path.join("home", "linus", "simple_game", "game.py")
    game_file_original = "/opt/task_12_setup_py_program.py"

    # check if game python file's content was changed
    with open(game_file, 'rb') as f1, open(game_file_original, 'rb') as f2:
        while True:
            b1 = f1.read(4096)
            b2 = f2.read(4096)
            if b1 != b2:
                sys.exit("The game.py file's code was changed, that is not allowed.")
            if not b1:
                break

    # check if pyton game file can be executed
    try:
        proc = subprocess.Popen(
            ['python', game_file, '-i', '4'],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )
        stdout, stderr = proc.communicate()
        if proc.returncode != 0:
            print(stderr)
            sys.exit("Can not start the game.")
    except Exception as e:
        print("Error:", e)
        sys.exit("Can not start the game.")

    sys.exit(0)
