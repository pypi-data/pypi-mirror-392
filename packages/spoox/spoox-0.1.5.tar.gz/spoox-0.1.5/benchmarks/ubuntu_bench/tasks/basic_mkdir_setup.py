import shutil
from pathlib import Path

if __name__ == "__main__":

    home = Path("/home/linus")

    # create more dummy directories
    (home / "Documents").mkdir()
    (home / "Photos").mkdir()
    (home / "Desktop").mkdir()
    (home / "Downloads").mkdir()

    # setup Maildir
    maildir_src = Path("/opt/tasks/task_15_16_setup_maildir")
    maildir_dst = home / "Maildir"
    shutil.copytree(maildir_src, maildir_dst)
