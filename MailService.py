from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from configparser import RawConfigParser
from os.path import basename
import smtplib
import ssl

class Mailer:
    
    def __init__(self, config):
        self.config = config
    
    def __joinFile(self, message, file_name):
        with open(file_name, "rb") as file:
            file_part = MIMEApplication(file.read(), Name=basename(file_name))
        # After the file is closed
        file_part['Content-Disposition'] = 'attachment; filename="%s"' % basename(file_name)
        message.attach(file_part)
    
    def sendMail(self, address_to, subject, content, files=None, address_from=None):
        address_from = address_from or self.config.get('SMTP', 'mailFrom')

        # MIME Multipart
        message = MIMEMultipart('alternative')
        message['Subject'] = subject
        message['From'] = address_from
        message['To'] = address_to
        html  = MIMEText(content, 'html', "utf-8")
        message.attach(html)

        # Text if mailer is not compatible
        #plain_text = "Mail in html format. please use another client to view it correctly."
        #plain = MIMEText(plain_text, 'plain')
        #message.attach(plain)
        
        # Join a single File or a list of files
        if isinstance(files, str):
            self.__joinFile(message, files)
        else :
            for f in files or []:
                self.__joinFile(message, f)

        # Send
        mail_server = smtplib.SMTP(self.config.get('SMTP', 'server'), self.config.get('SMTP', 'port'))
        mail_server.starttls()
        if self.config.getboolean('SMTP', 'authentification') :
            mail_server.login(self.config.get('SMTP', 'login'), self.config.get('SMTP', 'password'))
        mail_server.sendmail(address_from, address_to, message.as_string())
        mail_server.quit()
