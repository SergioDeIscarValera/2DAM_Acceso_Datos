from src.services.email.email_service_abc import EmailServiceABC
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import smtplib

class EmailServiceSmtplib(EmailServiceABC):
    def __init__(self, env):
        print("MAIL_SERVER: ", env['MAIL_SERVER'])
        self.mail_server = env['MAIL_SERVER']
        self.mail_port = env['MAIL_PORT']
        self.mail_username = env['MAIL_USERNAME']
        self.mail_password = env['MAIL_PASSWORD']


    async def send_email(self, to: str, subject: str, body: str, html_cuerpo: str = None) -> bool:
        server = smtplib.SMTP(self.mail_server, self.mail_port)
        server.starttls()
        server.login(self.mail_username, self.mail_password)
        mensaje = MIMEMultipart()
        mensaje['From'] = self.mail_username
        mensaje['To'] = to
        mensaje['Subject'] = subject
        mensaje.attach(MIMEText(body, 'plain'))

        if html_cuerpo:
            mensaje.attach(MIMEText(html_cuerpo, 'html'))
        
        try:
            server.sendmail(self.mail_username, to, mensaje.as_string())
            return True
        except Exception as e:
            print(e)
            return False
        finally:
            server.quit()
        

    async def send_verify_email(self, to: str, code:str) -> bool:
        subject = "Verify your email"
        url_verify = f"http://localhost:5000/users/verify/{to}?&code={code}"
        body = f"Click on the following link to verify your email and get access to the api, or copy and paste the following url in your browser: {url_verify}"
        html_body = f"<p>{body}</p><a href='{url_verify}'>Verify email</a>"
        return await self.send_email(to, subject, body, html_body)