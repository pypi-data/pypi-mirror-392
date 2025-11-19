import subprocess
import sys
from pathlib import Path

if __name__ == "__main__":

    home = Path("/home/linus")
    banned_file = home / "banned_ips.txt"
    user = "linus"

    if not banned_file.exists():
        sys.exit("banned_ips.txt not found")

    banned_file_text = banned_file.read_text()
    banned_file_lines = banned_file_text.splitlines()
    if not banned_file_lines:
        sys.exit("banned_ips.txt is empty")

    # IPs that are expected to appear (set in the setup script)
    expected_ips = {"192.168.1.10", "10.0.0.5", "172.16.0.2", "198.51.100.4"}
    if not all(ip in expected_ips for ip in banned_file_lines) and not all(ip in banned_file_text for ip in expected_ips):
        sys.exit("Not all expected IPs found in banned_ips.txt")

    # check if cron job is registered
    cmd = ["crontab", "-l", "-u", user]
    try:
        crontab_text = subprocess.check_output(cmd, text=True)
    except subprocess.CalledProcessError:
        sys.exit("Cron job not set up correctly.")
    if not "*/5" in crontab_text:
        sys.exit("Cron job not set up correctly.")

    sys.exit(0)
