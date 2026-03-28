from __future__ import annotations

import os
import smtplib
from email.mime.application import MIMEApplication
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


class EmailNotifier:
    def __init__(
        self,
        host: str,
        port: int,
        username: str,
        password: str,
        from_email: str,
        to_email: str,
    ) -> None:
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.from_email = from_email
        self.to_email = to_email

    @property
    def enabled(self) -> bool:
        return all([
            self.host,
            self.port,
            self.username,
            self.password,
            self.from_email,
            self.to_email,
        ])

    def send(self, subject: str, body: str, attachment_path: str | None = None) -> None:
        if not self.enabled:
            return

        msg = MIMEMultipart()
        msg["Subject"] = subject
        msg["From"] = self.from_email
        msg["To"] = self.to_email
        msg.attach(MIMEText(body, "plain", "utf-8"))

        if attachment_path and os.path.exists(attachment_path):
            with open(attachment_path, "rb") as f:
                part = MIMEApplication(f.read(), Name=os.path.basename(attachment_path))
            part["Content-Disposition"] = f'attachment; filename="{os.path.basename(attachment_path)}"'
            msg.attach(part)

        with smtplib.SMTP(self.host, self.port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.sendmail(self.from_email, [self.to_email], msg.as_string())
