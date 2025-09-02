import os
from dotenv import load_dotenv
import requests
import smtplib
from email.mime.text import MIMEText
from typing import Optional
from datetime import datetime


def _log_email_attempt(to_email: str, subject: str, success: bool, detail: str = "") -> None:
    try:
        with open("email.log", "a", encoding="utf-8") as f:
            ts = datetime.utcnow().isoformat()
            f.write(f"{ts}\tto={to_email}\tsubject={subject}\tsuccess={success}\tdetail={detail}\n")
    except Exception:
        pass


def send_verification_email(to_email: str, username: str, token: str) -> bool:
    # Load .env if present
    try:
        load_dotenv()
    except Exception:
        pass
    # Prefer Resend if configured
    api_key = os.getenv("RESEND_API_KEY")
    if api_key:
        try:
            resp = requests.post(
                "https://api.resend.com/emails",
                headers={
                    "Authorization": f"Bearer {api_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "from": os.getenv("RESEND_FROM", "Student Marks <onboarding@resend.dev>"),
                    "to": [to_email],
                    "subject": "Verify your Student Marks Analyzer account",
                    "text": f"Hi {username},\n\nYour verification code is: {token}\n\nEnter this code in the app to verify your email.",
                },
                timeout=15,
            )
            ok = 200 <= resp.status_code < 300
            _log_email_attempt(to_email, "Verify your Student Marks Analyzer account", ok, detail=f"Resend {resp.status_code} {resp.text[:200]}")
            return ok
        except Exception as e:
            _log_email_attempt(to_email, "Verify your Student Marks Analyzer account", False, detail=f"Resend error: {e}")
            # fall through to SMTP

    # Fall back to SMTP if Resend not configured or failed
    host = os.getenv("SMTP_HOST")
    port = int(os.getenv("SMTP_PORT", "587"))
    user = os.getenv("SMTP_USER")
    password = os.getenv("SMTP_PASSWORD")
    from_email = os.getenv("SMTP_FROM", user or "noreply@example.com")

    if not host or not user or not password:
        _log_email_attempt(to_email, "Verify your Student Marks Analyzer account", False, "No email provider configured")
        return False

    subject = "Verify your Student Marks Analyzer account"
    body = (
        f"Hi {username},\n\n"
        f"Your verification code is: {token}\n\n"
        f"Enter this code in the app to verify your email."
    )

    msg = MIMEText(body)
    msg["Subject"] = subject
    msg["From"] = from_email
    msg["To"] = to_email

    try:
        with smtplib.SMTP(host, port) as server:
            server.starttls()
            server.login(user, password)
            server.sendmail(from_email, [to_email], msg.as_string())
        _log_email_attempt(to_email, subject, True)
        return True
    except Exception as e:
        _log_email_attempt(to_email, subject, False, detail=str(e))
        return False


