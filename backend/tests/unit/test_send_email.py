import smtplib
from email.mime.text import MIMEText
from backend.src.config.smtp_config import SMTPConfig
from backend.src.email.email_service import EmailService

if __name__ == "__main__":
    mailer = EmailService()

    mailer.send_email_from_file(
        recipient="ss193461@student.pg.edu.pl",
        subject="Testowy e-mail",
        message_file="backend/src/email/templates/email_example.txt"
    )

    mailer.send_email_from_file(
        recipient="kulesz.agnieszka@wp.pl",
        subject="Testowy e-mail",
        message_file="backend/src/email/templates/email_rejection.txt"
    )

    mailer.send_email_from_file(
        recipient="kulesz.agnieszka@wp.pl",
        subject="Testowy e-mail",
        message_file="backend/src/email/templates/xx.txt"
    )