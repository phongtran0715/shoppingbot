import smtplib
from email.mime.text import MIMEText

smtp_ssl_host = 'smtp.gmail.com'
smtp_ssl_port = 465
username = 'USERNAME or EMAIL ADDRESS'
password = 'PASSWORD'
sender = 'ME@EXAMPLE.COM'

def send_email(recipients, subject, message):
	msg = MIMEText(message)
	msg['Subject'] = subject
	msg['From'] = sender
	msg['To'] = recipients

	server = smtplib.SMTP_SSL(smtp_ssl_host, smtp_ssl_port)
	server.login(username, password)
	server.sendmail(sender, targets, msg.as_string())
	server.quit()