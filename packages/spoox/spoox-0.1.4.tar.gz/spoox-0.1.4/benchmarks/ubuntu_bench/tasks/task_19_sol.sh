# 1. Install Postfix non-interactively
sudo debconf-set-selections <<< "postfix postfix/mailname string localdomain"
sudo debconf-set-selections <<< "postfix postfix/main_mailer_type string 'Local only'"
sudo DEBIAN_FRONTEND=noninteractive apt-get update -y
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y postfix

# 2. Configure Postfix to use Maildir format in ~/Maildir
sudo postconf -e "home_mailbox = Maildir/"
sudo postconf -e 'mailbox_command ='

# 3. Restart Postfix so changes take effect (work in docker)
sudo service postfix restart

# 4. Create the Maildir directory structure for your user
mkdir -p ~/Maildir/{new,cur,tmp}

# 5. Send a test email with subject MAIL_OK to yourself
{
  echo "Subject: MAIL_OK"
  echo "To: linus@localdomain"
  echo "From: tester@localdomain"
  echo
  echo "This is a test message."
} | sendmail -t
