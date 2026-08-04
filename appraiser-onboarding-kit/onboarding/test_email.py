#!/usr/bin/env python3
"""Prove email works before a real hire is waiting on it.

    python3 -m onboarding.test_email                  # sends to the owner address in config
    python3 -m onboarding.test_email --to me@you.com  # sends wherever you say

Two checks, in order: log in to the mail server, then actually send a message. Both have to
pass. Logging in proves the credentials; sending proves the message leaves the building.

Exit code 0 means a real message went out and you should expect it in the inbox within a
minute. Anything else means don't start onboarding anyone yet.
"""
import argparse, datetime, sys

from . import config as cfgmod, mailer


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="python3 -m onboarding.test_email",
        description="Check that this office can actually send email.")
    p.add_argument("--to", default=None,
                   help="Where to send the test. Defaults to your owner address.")
    p.add_argument("--check-only", action="store_true",
                   help="Log in to verify the credentials, but don't send anything.")
    a = p.parse_args(argv)

    try:
        cfg = cfgmod.load()
    except cfgmod.ConfigError as e:
        print(f"\n{e}\n")
        return 1

    mode = cfg.get("email", {}).get("mode", "none")
    to = a.to or cfg.get("people", {}).get("owner", {}).get("email", "")
    print(f"\nOffice   : {cfg['office']['name']}")
    print(f"Mode     : {mode}")
    if mode == "smtp":
        s = cfg["email"]["smtp"]
        print(f"Server   : {s.get('host')}:{s.get('port')} as {s.get('username')}")
    print(f"Sending  : {to or '(no address)'}\n")

    ok, message = mailer.check_login(cfg)
    print(("  ✓ " if ok else "  ✗ ") + message + "\n")
    if not ok:
        print("Nothing was sent. Fix the above, then run this again.\n")
        return 1
    if a.check_only:
        return 0

    if "@" not in to:
        print("No address to send to. Pass --to, or fill in people.owner.email.\n")
        return 1

    stamp = datetime.datetime.now().strftime("%Y-%m-%d %I:%M %p")
    subject = f"Onboarding kit test — {cfg['office']['name']}"
    body = (f"This is a test from your onboarding system, sent {stamp}.\n\n"
            f"If you're reading it, email delivery works and new hires will get their "
            f"welcome links.\n\n"
            f"Nothing else happened — no hire was created and nothing was filed.\n")

    if not mailer.send(cfg, to, subject, body):
        print("\n  ✗ Login worked but the send failed. The error above is from the mail "
              "server.\n    Do not start onboarding anyone until a test message arrives.\n")
        return 2

    print(f"  ✓ Test message sent to {to}.\n")
    print("Check that inbox — and the spam folder. If it isn't there in a few minutes, the "
          "server\naccepted it but something downstream dropped it, which is worth sorting "
          "out before\na real hire is waiting on a link.\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
