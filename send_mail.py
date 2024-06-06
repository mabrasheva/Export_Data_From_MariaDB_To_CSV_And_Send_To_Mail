import os
import re
import logging
import smtplib
from email import encoders
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from calc_date_time import file_creation_datetime, date_and_time_format

smtp_server = os.getenv("smtp_server")
smtp_port = int(os.getenv("smtp_port"))
path = os.getenv("path")
attachment_file_path = Path(path)  # fill the attachment path. Example: "./Folder"
sender_email = os.getenv("sender_email")
receiver_email = os.getenv("receiver_email")
password = os.getenv("password")
email_html_body_content_message = os.getenv("email_html_body_content_message")
email_subject = f'{os.getenv("email_subject")} {file_creation_datetime}'

current_directory = Path(os.getcwd())

body_html = f"""\
    <html>
      <body>
        <p>{email_html_body_content_message}</p>
      </body>
    </html>
    """

# pattern = re.compile(r"(?P<file_name>[\w-]+)\.(?P<file_extension>[a-z0-9]+)$")
pattern = re.compile(fr"(?P<file_name>[\w-]+{file_creation_datetime})\.(?P<file_extension>[a-z0-9]+)$")
searched_file_extensions = ["txt", "csv", "xlsx"]
log_filename = "./send_mail.log"
logging.basicConfig(filename=log_filename, level=logging.DEBUG)

message = MIMEMultipart()
message['From'] = sender_email
message['To'] = receiver_email
message['Subject'] = email_subject
message.attach(MIMEText(body_html, "html"))


def send_mail():
    try:
        with smtplib.SMTP(smtp_server, smtp_port) as session:
            session.starttls()
            session.login(sender_email, password)
            session.sendmail(sender_email, receiver_email, message.as_string())
            session.quit()
    except (OSError, smtplib.SMTPException) as mail_err:
        logging.exception(f"{date_and_time_format()} Error occurred during email session: {mail_err}\n")


def create_email_attachment_object(path: Path, attachment_file: str):
    attachment = MIMEBase('application', "octet-stream")
    with open(f"{path}/{attachment_file}", 'rb') as file:  # Set file content as attachment payload
        attachment.set_payload(file.read())
    encoders.encode_base64(attachment)  # Encode attachment file in base64
    attachment.add_header('Content-Disposition', f'attachment;filename = {attachment_file}')
    return attachment


def message_attach_files(attachment_file_path: Path):
    try:
        for file in os.scandir(str(attachment_file_path.resolve())):
            if os.path.isdir(file.name):  # If current item is dir
                continue
            match = re.search(pattern, file.name)
            if match and match["file_extension"] in searched_file_extensions:
                attachment = create_email_attachment_object(attachment_file_path, file.name)
                message.attach(attachment)
    except Exception as error:
        logging.exception(f"### {date_and_time_format()}: Error occurred when attaching files:\n {error}\n")


message_attach_files(attachment_file_path)
send_mail()
