import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from os.path import basename

from Utils.log import log

from Email.config import EMAIL_PASSWORD, EMAIL_LOGIN, SMTP_SERVER, SMTP_PORT, email_login_password


class EmailSending:
    def __init__(self, subject='Новый отзыв на сайте.', from_email=EMAIL_LOGIN, to='', cc='', bcc='',
                 text='', html='', smtp_server=SMTP_SERVER, smtp_port=SMTP_PORT,
                 login=EMAIL_LOGIN, password=EMAIL_PASSWORD, manager=None, files_path: list = []):
        """

        :type text: Plain text Email, if html not support
        """
        self.subject = subject
        self.from_email = from_email
        self.to_address = []
        self.to = to
        self.cc = cc
        self.bcc = bcc
        for x in [self.to, self.cc, self.bcc]:
            if type(x) is list:
                self.to_address.extend(x)
            elif x != '':
                self.to_address.append(x)

        self.text = text
        self.html = html
        self.smtp_server = smtp_server
        self.smtp_port = smtp_port
        self.user = login
        self.password = password
        if manager:
            try:
                self.password = email_login_password[manager]
                self.user = manager
                self.from_email = manager
            except KeyError:
                pass
        self.files = files_path

    def send_email(self):
        msg = MIMEMultipart()
        msg['From'] = self.from_email
        msg['Subject'] = self.subject
        if type(self.to) is str:
            msg['To'] = self.to
        else:
            msg['To'] = ','.join(self.to)

        if type(self.cc) is str:
            msg['Cc'] = self.cc
        else:
            msg['Cc'] = ','.join(self.cc)

        if type(self.bcc) is str:
            msg['Bcc'] = self.bcc
        else:
            msg['Bcc'] = ','.join(self.bcc)

        msg.attach(MIMEText(self.text, 'plain'))
        msg.attach(MIMEText(self.html, 'html'))

        for f in self.files:
            with open(f, "rb") as fil:
                part = MIMEApplication(
                    fil.read(),
                    Name=basename(f)
                )
            # After the file is closed
            part['Content-Disposition'] = 'attachment; filename="%s"' % basename(f)
            msg.attach(part)

        smtp = smtplib.SMTP_SSL(self.smtp_server, self.smtp_port)
        smtp.login(self.user, self.password)
        smtp.sendmail(from_addr=self.user, to_addrs=self.to_address, msg=msg.as_string())
        smtp.quit()
        log.info(f'Email send {self.to_address}')
        return f'Email send {self.to_address}'
