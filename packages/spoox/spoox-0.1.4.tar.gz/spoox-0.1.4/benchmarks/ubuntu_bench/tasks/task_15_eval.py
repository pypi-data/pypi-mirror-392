import sys
from datetime import date, timedelta
from pathlib import Path


def calculate_pete_age():
    """Calculating Pete's age - born in 1990 and his birthday is next wednesday"""

    today = date.today()
    birth_year = 1990
    current_year = today.year

    # Find next Wednesday
    days_ahead = (2 - today.weekday() + 7) % 7  # 2 = Wednesday (Mon=0, Tue=1, Wed=2, ...)
    if days_ahead == 0:
        days_ahead = 7  # If today is Wednesday, "next Wednesday" is in 7 days
    next_wednesday = today + timedelta(days=days_ahead)

    # Pete's birthday this year is on next Wednesday's date (but in 1990)
    birthday_this_year = date(current_year, next_wednesday.month, next_wednesday.day)

    # Check if Pete has had his birthday this year
    if today < birthday_this_year:
        age = current_year - birth_year - 1
    else:
        age = current_year - birth_year

    return age


if __name__ == "__main__":

    home = Path("/home/linus")
    sol_file = home / "pete_age.txt"
    maildir_dst_new_dir = home / "Maildir" / "new"
    maildir_dst_cur_dir = home / "Maildir" / "cur"
    maildir_src_new_dir = Path("/opt/task_15_16_setup_maildir/new")
    maildir_src_cur_dir = Path("/opt/task_15_16_setup_maildir/cur")

    # check 'pete_age' solution file and validate content
    if not sol_file.is_file():
        sys.exit("File pete_age.txt not found.")
    with sol_file.open() as f:
        content = f.read().lower()
        if str(calculate_pete_age()) not in content:
            sys.exit("Incorrect age.")

    # check if Maildir 'new' dir is empty
    if any(maildir_dst_new_dir.iterdir()):
        sys.exit(f"There are still mails in my inbox.")

    # check if all mails in 'new' are copied to 'cur'
    for mail_file in maildir_src_new_dir.iterdir():
        if mail_file.is_file():
            target_file = maildir_dst_cur_dir / mail_file.name
            if not target_file.exists():
                sys.exit(f"There are some mails missing in my Maildir cur.")

    # check previous mails in 'cur' are still there
    for mail_file in maildir_src_cur_dir.iterdir():
        if mail_file.is_file():
            target_file = maildir_dst_cur_dir / mail_file.name
            if not target_file.exists():
                sys.exit(f"There are some mails missing in my Maildir cur.")

    sys.exit(0)
