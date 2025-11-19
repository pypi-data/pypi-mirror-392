# 1. execute sample solution bash script for failed SSH login attempt filtering
bash /opt/update_banned_ips.sh

# 2. configure cron job
( crontab -l 2>/dev/null; printf '%s\n' "*/5 * * * * $HOME/update_banned_ips.sh" ) | crontab -