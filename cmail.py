import smtplib
from email.message import EmailMessage
def sendmail(to, subject, body):
    # Correct SMTP server address
    server = smtplib.SMTP_SSL('smtp.gmail.com', 465)
    # Use your actual credentials
    email_address = 'yourgmail'
    email_password = 'dmailpasscodekey'  # Use App Password if 2-Step Verification is enabled
    try:
        server.login(email_address, email_password)
        msg = EmailMessage()
        msg['From'] = email_address
        msg['To'] = to
        msg['Subject'] = subject
        msg.set_content(body)
        server.send_message(msg)
        print("Email sent successfully!")
    except smtplib.SMTPAuthenticationError as e:
        print(f"Authentication failed: {e}")
    finally:
        server.quit()