"""Send email three ways, per config: 'none' (print it — testing and small offices that
prefer to copy/paste), 'smtp' (any mail server; a Gmail app password works), or 'gog'
(the gog CLI, for offices already using it).

Every caller must survive mail being down: sending is best-effort everywhere except the
welcome link, where the caller checks the return and tells the human it didn't go.
"""
import os, shutil, smtplib, subprocess
from email.message import EmailMessage
from email.utils import formataddr

from . import config as cfgmod


def send(cfg, to, subject, body, attachments=None, cc=None):
    """Returns True if the message was handed off (or printed, in 'none' mode)."""
    mode = cfg.get("email", {}).get("mode", "none")
    if mode == "none":
        print("\n" + "=" * 60)
        print(f"EMAIL (not sent — email.mode is 'none')")
        print(f"To: {to}" + (f"  Cc: {cc}" if cc else ""))
        print(f"Subject: {subject}")
        print("-" * 60)
        print(body)
        if attachments:
            print(f"[would attach: {', '.join(os.path.basename(a) for a in attachments)}]")
        print("=" * 60)
        return True
    if mode == "smtp":
        return _smtp(cfg, to, subject, body, attachments, cc)
    if mode == "gog":
        return _gog(cfg, to, subject, body, attachments, cc)
    return False


def _smtp(cfg, to, subject, body, attachments, cc):
    s = cfg["email"]["smtp"]
    password = os.environ.get(s.get("password_env", ""), "")
    if not (s.get("username") and password):
        print("mailer: smtp mode but username or password env var missing")
        return False
    msg = EmailMessage()
    msg["From"] = formataddr((cfg["email"].get("from_name", ""), s["username"]))
    msg["To"] = to
    if cc:
        msg["Cc"] = cc
    msg["Subject"] = subject
    msg.set_content(body)
    for path in (attachments or []):
        with open(path, "rb") as f:
            data = f.read()
        maintype, subtype = ("application", "pdf") if path.lower().endswith(".pdf") \
            else ("application", "octet-stream")
        msg.add_attachment(data, maintype=maintype, subtype=subtype,
                           filename=os.path.basename(path))
    try:
        with smtplib.SMTP(s.get("host", "smtp.gmail.com"), int(s.get("port", 587)),
                          timeout=60) as srv:
            srv.starttls()
            srv.login(s["username"], password)
            srv.send_message(msg)
        return True
    except Exception as e:
        print(f"mailer: smtp send failed: {e}")
        return False


def _gog(cfg, to, subject, body, attachments, cc):
    g = cfg["email"]["gog"]
    args = [g.get("binary", "gog"), "gmail", "send",
            "--account", g.get("account", ""), "--to", to,
            "--subject", subject, "--body", body]
    if cc:
        args += ["--cc", cc]
    for a in (attachments or []):
        args += ["--attach", a]
    try:
        r = subprocess.run(args, capture_output=True, text=True, timeout=120)
        if r.returncode != 0:
            print(f"mailer: gog send failed: {r.stderr.strip()[:200]}")
        return r.returncode == 0
    except Exception as e:
        print(f"mailer: gog send failed: {e}")
        return False


def check_login(cfg):
    """Connect and log in without sending anything. Returns (ok, message) where the
    message is written for an office owner, not a sysadmin — the point is that they find
    out mail is broken now, not the morning a real hire is waiting on a link."""
    mode = cfg.get("email", {}).get("mode", "none")
    if mode == "none":
        return False, ("email.mode is 'none', so nothing is ever sent — the system prints "
                       "messages for you to copy and paste instead. Set it to 'smtp' in "
                       "config/office.json to send for real.")
    if mode == "gog":
        g = cfg["email"]["gog"]
        binary = g.get("binary", "gog")
        if not (shutil.which(binary) or os.path.exists(binary)):
            return False, f"email.mode is 'gog' but '{binary}' isn't installed on this machine."
        return True, f"gog CLI found at {shutil.which(binary) or binary}. Sending a real test is the only full check."
    s = cfg["email"]["smtp"]
    env = s.get("password_env", "ONBOARDING_SMTP_PASSWORD")
    password = os.environ.get(env, "")
    if not s.get("username"):
        return False, "email.smtp.username is empty in config/office.json."
    if not password:
        return False, (f"The environment variable {env} isn't set in this shell, so there's "
                       f"no password to log in with.\n  Set it with:  export {env}='your app password'")
    host, port = s.get("host", "smtp.gmail.com"), int(s.get("port", 587))
    try:
        with smtplib.SMTP(host, port, timeout=30) as srv:
            srv.starttls()
            srv.login(s["username"], password)
        return True, f"Logged in to {host}:{port} as {s['username']}."
    except smtplib.SMTPAuthenticationError:
        hint = ("\n  Gmail rejects your normal account password here. You need a 16-character "
                "App Password:\n  Google Account → Security → 2-Step Verification → App "
                "passwords. Paste it with no spaces."
                if "gmail" in host else
                "\n  The server accepted the connection but rejected the username or password.")
        return False, f"{host} refused the login for {s['username']}.{hint}"
    except (smtplib.SMTPConnectError, OSError) as e:
        return False, (f"Couldn't reach {host}:{port} — {e}.\n  Check the host and port in "
                       f"config/office.json (587 with STARTTLS is the usual pair), and that "
                       f"this machine can get out on that port.")
    except Exception as e:
        return False, f"{type(e).__name__}: {e}"


def notify_owner(cfg, subject, body, attachments=None):
    """Owner always hears about completions. Bookkeeper is cc'd only on tax paperwork
    (the caller decides). Best-effort by design."""
    return send(cfg, cfg["people"]["owner"]["email"], subject, body, attachments)
