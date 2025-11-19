import getpass
import re
import socket
import subprocess
import sys
from time import sleep
from pathlib import Path
from email.utils import make_msgid

if __name__ == "__main__":

    home = Path("/home/linus")
    maildir_new = home / "Maildir" / "new"
    maildir_cur = home / "Maildir" / "cur"

    # check if expected Maildir struc still exists
    if not maildir_new.exists():
        sys.exit("Maildir new directory is missing.")
    if not maildir_cur.exists():
        sys.exit("Maildir cur directory is missing.")

    # send test mail
    mail_id = make_msgid(domain="localdomain")
    user = getpass.getuser()
    hostname = socket.gethostname()
    mail = "\r\n".join([
        f"From: eval@localdomain",
        f"To: linus@localdomain",
        f"Subject: MAIL_EVAL",
        f"Message-ID: {mail_id}",
        ""
        "This is a local delivery test message.",
        "",
    ])
    proc = subprocess.run(["sendmail", "-t", "-oi"], input=mail.encode("utf-8"), check=True, user='linus')
    sleep(4)

    # check if MAIL_OK and MAIL_EVAL are present in inbox
    found_mail_ok = False
    found_mail_eval = False
    pattern_mail_ok = re.compile(r"Subject:\s*MAIL_OK")
    pattern_mail_eval = re.compile(r"Subject:\s*MAIL_EVAL")
    pattern_mail_eval_id = re.compile(rf"{mail_id}")
    for f in maildir_new.glob("*"):
        try:
            text = f.read_text(errors="ignore")
        except Exception:
            continue
        if pattern_mail_ok.search(text, re.IGNORECASE):
            found_mail_ok = True
        if pattern_mail_eval.search(text, re.IGNORECASE) and pattern_mail_eval_id.search(text, re.IGNORECASE):
            found_mail_eval = True
    if not found_mail_ok:
        sys.exit("Found no test mail with subject MAIL_OK.")
    if not found_mail_ok:
        sys.exit("Could not sent a mail locally that ended up in my Maildir.")

    sys.exit(0)
