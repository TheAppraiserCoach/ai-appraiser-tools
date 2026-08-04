#!/usr/bin/env python3
"""Start a hire: one command, and they get their personal onboarding link.

    python3 -m onboarding.send_welcome \
        --first Jane --last Doe --email jane@example.com --start 2026-08-17 --pay "$22/hour"

That is the whole owner-facing workflow. Everything the hire needs — training, the
agreement, the tax forms — hangs off the link this sends. The link carries their identity
in the query string, so there is no account to create and nothing for them to retype, and
the server keys progress by email so switching from phone to laptop resumes instead of
restarting.

Two rules this module holds to, both learned from onboarding systems that failed quietly:
  - Never send a document with a hole in it. If a {{placeholder}} didn't resolve, we
    refuse to send rather than mail someone a letter with "{{owner_phone}}" in it.
  - Never report a send we didn't make. mailer.send() returns whether the message was
    actually handed off; if it wasn't, we say so and print the email for copy/paste
    instead of exiting 0 and letting the owner assume it went.
"""
import argparse, datetime, json, os, re, sys, tempfile, urllib.parse

from . import config as cfgmod, mailer, storage as storemod

TEMPLATE = os.path.join(cfgmod.ROOT, "content", "emails", "welcome.md")


# What an owner actually types. Nobody should have to remember "contractor_1099" — this
# maps the words a person says out loud onto the config keys. Exact config keys still win.
ALIASES = {
    "employee": "w2_employee", "w2": "w2_employee", "w-2": "w2_employee",
    "w2employee": "w2_employee", "staff": "w2_employee", "hourly": "w2_employee",
    "salaried": "w2_employee", "fulltime": "w2_employee", "full-time": "w2_employee",
    "contractor": "contractor_1099", "1099": "contractor_1099", "ic": "contractor_1099",
    "independent": "contractor_1099", "independentcontractor": "contractor_1099",
    "feeappraiser": "contractor_1099", "fee": "contractor_1099",
    "foreign": "contractor_foreign", "w8": "contractor_foreign",
    "w-8ben": "contractor_foreign", "w8ben": "contractor_foreign",
    "overseas": "contractor_foreign", "international": "contractor_foreign",
}


def resolve_hire_type(cfg, spoken):
    """Turn what the owner typed into an enabled hire-type key, or raise with the options.
    Returns None when nothing was given (the caller decides whether to ask)."""
    enabled = cfgmod.enabled_hire_types(cfg)
    if not spoken:
        return next(iter(enabled)) if len(enabled) == 1 else None
    raw = spoken.strip()
    key = raw if raw in enabled else ALIASES.get(re.sub(r"[\s_]+", "", raw.lower()))
    if key in enabled:
        return key
    if key in cfg.get("hire_types", {}):
        raise cfgmod.ConfigError(
            f"'{spoken}' is the {cfg['hire_types'][key].get('label', key)} track, which is "
            f"turned off in config/office.json.\nSet hire_types.{key}.enabled to true to "
            f"use it. Currently on: {', '.join(describe_types(cfg))}.")
    raise cfgmod.ConfigError(
        f"I don't know the hire type '{spoken}'.\nUse one of: "
        f"{', '.join(describe_types(cfg))}.")


def describe_types(cfg):
    """Human-facing menu entries: the plain word first, the config key in parentheses."""
    words = {"w2_employee": "employee", "contractor_1099": "contractor",
             "contractor_foreign": "foreign contractor"}
    return [f"{words.get(k, k)} ({k})" for k in cfgmod.enabled_hire_types(cfg)]


def ask_hire_type(cfg):
    """More than one track is on and the owner didn't say which. Ask, if there's someone
    there to ask. In a script or a cron job stdin isn't a terminal, so we refuse instead of
    hanging forever on input() or guessing a tax classification."""
    enabled = list(cfgmod.enabled_hire_types(cfg))
    if not sys.stdin.isatty():
        print("\nIs this person an employee or a contractor? Say which with --type:\n  "
              + "\n  ".join(f"--type {w}" for w in describe_types(cfg)) + "\n")
        return None
    print("\nIs this person an employee or a contractor?\n")
    for i, key in enumerate(enabled, 1):
        ht = cfg["hire_types"][key]
        kind = "1099 — no withholding" if cfgmod.is_contractor(ht) else "W-2 — taxes withheld"
        print(f"  {i}. {ht.get('label', key)}  ({kind}; {', '.join(ht.get('tax_forms', [])) or 'no forms'})")
    print()
    for _ in range(3):
        try:
            answer = input("Which one? (number, or type 'employee' / 'contractor'): ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            return None
        if answer.isdigit() and 1 <= int(answer) <= len(enabled):
            return enabled[int(answer) - 1]
        try:
            return resolve_hire_type(cfg, answer)
        except cfgmod.ConfigError as e:
            print(f"  {e.args[0].splitlines()[0]}")
    return None


def onboarding_link(cfg, hire):
    """The hub URL with identity attached — see ingestParams() in web/hub.html."""
    base = (cfg.get("server", {}).get("public_url") or "").rstrip("/")
    q = urllib.parse.urlencode({"fn": hire["first_name"], "ln": hire["last_name"],
                                "em": hire["email"], "sd": hire["start_date"],
                                "ht": hire["hire_type"]})
    return f"{base}/onboarding?{q}"


def compose(cfg, hire):
    """Render the welcome email. Returns (subject, body); raises if anything is unresolved."""
    raw = open(TEMPLATE).read()
    ht = cfgmod.hire_type(cfg, hire["hire_type"])
    forms = ht.get("tax_forms", [])
    if len(forms) > 1:
        form_list = ", ".join(forms[:-1]) + f" and {forms[-1]}"
    else:
        form_list = forms[0] if forms else "the forms we'll send separately"

    modules = cfgmod.training_modules(cfg, hire["hire_type"])
    contractor = cfgmod.is_contractor(ht)
    subs = cfgmod.substitutions(cfg)

    # Pay is optional: some offices put it in the offer letter and don't want it restated
    # here. When it's absent the paragraph disappears cleanly. When it's present the
    # wording has to match the track — telling a 1099 contractor "how to submit your
    # hours" contradicts the agreement they're about to sign.
    if not hire.get("pay"):
        pay_line = ""
    elif contractor:
        pay_line = (f"Your fee is {hire['pay']}. Module {len(modules)} covers invoicing — "
                    f"how to send it, when it's due, and when payment goes out.\n\n")
    else:
        pay_line = (f"Your pay is {hire['pay']}, {subs['pay_cadence']}. "
                    f"Module {len(modules)} walks through how to submit your hours.\n\n")

    extra = {
        "first_name": hire["first_name"],
        "last_name": hire["last_name"],
        "full_name": f"{hire['first_name']} {hire['last_name']}",
        "start_date": hire["start_date"],
        "onboarding_link": onboarding_link(cfg, hire),
        "module_count": str(len(modules)),
        "tax_form_list": form_list,
        "pay_line": pay_line,
        # A contractor doesn't have a "first day" and isn't "joining" the office.
        "engagement_line": (
            f"You're working with {subs['office_name']} as an independent contractor, "
            f"starting {hire['start_date']}."
            if contractor else
            f"You're joining {subs['office_name']} as {subs['role_title']}, "
            f"starting {hire['start_date']}."),
        "before_when": "before your first assignment" if contractor else "before your first day",
    }
    filled = cfgmod.fill(raw, cfg, extra)
    holes = cfgmod.unresolved(filled)
    if holes:
        raise cfgmod.ConfigError(
            "The welcome email still has unresolved placeholders, so it wasn't sent: "
            + ", ".join("{{%s}}" % h for h in holes)
            + "\nFill these in in config/office.json.")

    lines = filled.splitlines()
    if not lines or not lines[0].lower().startswith("subject:"):
        raise cfgmod.ConfigError(
            f"{TEMPLATE} must start with a 'Subject: ...' line.")
    subject = lines[0].split(":", 1)[1].strip()
    body = "\n".join(lines[1:]).lstrip("\n")
    return subject, body


def file_hire_record(store, hire):
    """Put a hire.json in the hire's folder so pay and start date are on record from day
    one, not only after they finish. The CSV/Sheet tracker has a fixed set of columns;
    this is where the rest of what we know about the hire lives."""
    work = tempfile.mkdtemp(prefix="onbkit_")
    try:
        path = os.path.join(work, "hire.json")
        record = dict(hire)
        record["welcome_sent"] = datetime.datetime.now().isoformat(timespec="seconds")
        with open(path, "w") as f:
            json.dump(record, f, indent=2)
        return store.put(hire, path)
    finally:
        import shutil
        shutil.rmtree(work, ignore_errors=True)


def main(argv=None):
    p = argparse.ArgumentParser(
        prog="python3 -m onboarding.send_welcome",
        description="Email a new hire their personal onboarding link.")
    p.add_argument("--first", required=True, help="First name")
    p.add_argument("--last", required=True, help="Last name")
    p.add_argument("--email", required=True, help="Where the welcome link goes")
    p.add_argument("--start", required=True, metavar="YYYY-MM-DD", help="Start date")
    p.add_argument("--pay", default="", help='Optional, e.g. "$22/hour" or "$52,000/year"')
    p.add_argument("--type", dest="hire_type", default=None, metavar="employee|contractor",
                   help="employee (W-2) or contractor (1099). If you leave it off and both "
                        "are turned on, you'll be asked.")
    p.add_argument("--dry-run", action="store_true",
                   help="Print the email and the link; file nothing, send nothing")
    a = p.parse_args(argv)

    try:
        cfg = cfgmod.load()
    except cfgmod.ConfigError as e:
        print(f"\n{e}\n")
        return 1

    if "@" not in a.email:
        print(f"'{a.email}' doesn't look like an email address.")
        return 1
    try:
        datetime.date.fromisoformat(a.start)
    except ValueError:
        print(f"--start must be YYYY-MM-DD, got '{a.start}'.")
        return 1

    try:
        hire_type_key = resolve_hire_type(cfg, a.hire_type)
    except cfgmod.ConfigError as e:
        print(f"\n{e}\n")
        return 1
    if not hire_type_key:
        hire_type_key = ask_hire_type(cfg)
    if not hire_type_key:
        return 1
    try:
        ht = cfgmod.hire_type(cfg, hire_type_key)
    except cfgmod.ConfigError as e:
        print(f"\n{e}\n")
        return 1

    hire = {"first_name": a.first.strip(), "last_name": a.last.strip(),
            "email": a.email.strip(), "start_date": a.start,
            "hire_type": hire_type_key, "pay": a.pay.strip()}

    try:
        subject, body = compose(cfg, hire)
    except cfgmod.ConfigError as e:
        print(f"\n{e}\n")
        return 1

    if a.dry_run:
        print(f"[dry run — nothing sent, nothing filed]\n")
        print(f"To: {hire['email']}\nSubject: {subject}\n{'-' * 60}\n{body}")
        return 0

    store = storemod.get(cfg)
    file_hire_record(store, hire)
    store.upsert(hire, agreement="not started", tax_forms="not started",
                 training="not started", complete="no")

    sent = mailer.send(cfg, hire["email"], subject, body,
                       cc=cfg.get("people", {}).get("owner", {}).get("email"))

    print(f"\n{hire['first_name']} {hire['last_name']} ({ht['label']}) — "
          f"start {hire['start_date']}" + (f", {hire['pay']}" if hire["pay"] else ""))
    print(f"  filed to   : {store.describe()}")
    print(f"  their link : {onboarding_link(cfg, hire)}")
    if sent:
        mode = cfg.get("email", {}).get("mode", "none")
        if mode == "none":
            print("  email      : NOT SENT — email.mode is 'none'. The message is printed "
                  "above; copy/paste it, or set email.mode in config/office.json.")
        else:
            print(f"  email      : sent to {hire['email']} via {mode}")
    else:
        print("  email      : FAILED TO SEND. The hire is on file and the link above is "
              "live — send it by hand, then fix email in config/office.json.")
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
