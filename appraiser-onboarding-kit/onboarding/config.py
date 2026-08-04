"""Load and validate the office configuration.

Everything office-specific lives in config/office.json. Nothing else in this codebase
should contain your office name, your people, or your folder IDs — if you find yourself
editing a .py or .html file to change a name, that's a bug in this kit, not in your setup.
"""
import json, os, re, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONFIG_PATH = os.path.join(ROOT, "config", "office.json")
EXAMPLE_PATH = os.path.join(ROOT, "config", "office.example.json")


class ConfigError(Exception):
    """Raised with a message written for a human, not a stack trace."""


def _strip_comments(obj):
    """Drop the _comment / _README keys used to document the example file."""
    if isinstance(obj, dict):
        return {k: _strip_comments(v) for k, v in obj.items()
                if not k.startswith("_")}
    if isinstance(obj, list):
        return [_strip_comments(v) for v in obj]
    return obj


def load(path=None):
    path = path or CONFIG_PATH
    if not os.path.exists(path):
        raise ConfigError(
            f"No config found at {path}.\n"
            f"Copy config/office.example.json to config/office.json and fill it in.\n"
            f"  cp config/office.example.json config/office.json")
    try:
        raw = json.load(open(path))
    except json.JSONDecodeError as e:
        raise ConfigError(
            f"config/office.json isn't valid JSON — {e.msg} on line {e.lineno}.\n"
            f"Usually this is a missing comma, or a trailing comma after the last item.")
    cfg = _strip_comments(raw)
    validate(cfg)
    return cfg


def validate(cfg):
    """Fail loudly and in plain language, before a real hire hits a half-configured system."""
    problems = []

    def need(path, why):
        cur = cfg
        for part in path.split("."):
            if not isinstance(cur, dict) or part not in cur or cur[part] in ("", None):
                problems.append(f"  - {path} is empty. {why}")
                return None
            cur = cur[part]
        return cur

    need("office.name", "It's the name your new hire sees on every screen and document.")
    need("office.role_title", "The job title that goes on the agreement, e.g. 'Appraisal Trainee'.")
    owner_email = need("people.owner.email", "Someone has to receive the completed paperwork.")

    if owner_email and "@" not in str(owner_email):
        problems.append("  - people.owner.email doesn't look like an email address.")

    enabled = [k for k, v in cfg.get("hire_types", {}).items() if v.get("enabled")]
    if not enabled:
        problems.append("  - No hire types are enabled. Turn on at least one in hire_types "
                        "(w2_employee, contractor_1099, or contractor_foreign).")

    for key in enabled:
        ht = cfg["hire_types"][key]
        agreement = ht.get("agreement")
        if agreement:
            p = os.path.join(ROOT, "content", "agreements", agreement)
            if not os.path.exists(p):
                problems.append(f"  - hire_types.{key} points at content/agreements/"
                                f"{agreement}, which doesn't exist.")

    # office-wide module list, plus any per-track override
    module_lists = {"training.modules": cfg.get("training", {}).get("modules", [])}
    for key in enabled:
        override = cfg["hire_types"][key].get("training_modules")
        if override:
            module_lists[f"hire_types.{key}.training_modules"] = override
    for where, mods in module_lists.items():
        if not mods:
            problems.append(f"  - {where} is empty — a hire would get no training at all.")
        for m in mods:
            p = os.path.join(ROOT, "content", "training", m)
            if not os.path.exists(p):
                problems.append(f"  - training module content/training/{m} is listed in "
                                f"{where} but the file doesn't exist.")

    storage = cfg.get("storage", {})
    if storage.get("mode") not in ("local", "google"):
        problems.append("  - storage.mode must be either \"local\" or \"google\".")
    if storage.get("mode") == "google":
        for k in ("account", "employees_folder_id", "tracker_sheet_id"):
            if not storage.get("google", {}).get(k):
                problems.append(f"  - storage.mode is \"google\" but storage.google.{k} is empty.")

    email = cfg.get("email", {})
    if email.get("mode") not in ("none", "smtp", "gog"):
        problems.append("  - email.mode must be \"none\", \"smtp\", or \"gog\".")
    if email.get("mode") == "smtp":
        if not email.get("smtp", {}).get("username"):
            problems.append("  - email.mode is \"smtp\" but email.smtp.username is empty.")
        env = email.get("smtp", {}).get("password_env")
        if env and not os.environ.get(env):
            problems.append(f"  - email.mode is \"smtp\" but the environment variable "
                            f"{env} isn't set, so there's no password to log in with.")

    if problems:
        raise ConfigError("Your config/office.json needs a few fixes:\n" + "\n".join(problems))


def enabled_hire_types(cfg):
    return {k: v for k, v in cfg.get("hire_types", {}).items() if v.get("enabled")}


def hire_type(cfg, key):
    ht = cfg.get("hire_types", {}).get(key)
    if not ht or not ht.get("enabled"):
        avail = ", ".join(enabled_hire_types(cfg)) or "(none enabled)"
        raise ConfigError(f"Unknown or disabled hire type '{key}'. Enabled: {avail}")
    return ht


def _contractor_pay(cfg):
    """Invoicing placeholders for the 1099 track, with the W-2 payroll settings as the
    fallback. Kept separate from substitutions() so contractor_pay_is_default() can tell
    an office it never filled these in."""
    pay = cfg.get("payroll", {})
    c = pay.get("contractor", {}) or {}
    return {
        "invoice_cadence": c.get("cadence") or pay.get("cadence", ""),
        "invoice_deadline": c.get("deadline") or pay.get("deadline", ""),
        "invoice_method": c.get("submit_method") or pay.get("submit_method", ""),
        "invoice_pay_lag": c.get("pay_lag") or pay.get("pay_lag", ""),
    }


def contractor_pay_is_default(cfg):
    """True when a contractor track is enabled but payroll.contractor was never filled in,
    so contractors would be shown the employee timesheet wording."""
    if not any(is_contractor(v) for v in enabled_hire_types(cfg).values()):
        return False
    c = cfg.get("payroll", {}).get("contractor", {}) or {}
    return not any(c.get(k) for k in ("cadence", "deadline", "submit_method", "pay_lag"))


def is_contractor(ht):
    """A track is a contractor track if it says so, else inferred from its tax forms.
    Explicit beats inferred: an office can set "contractor": true/false on any track."""
    if "contractor" in ht:
        return bool(ht["contractor"])
    forms = {f.upper() for f in ht.get("tax_forms", [])}
    return bool(forms & {"W-9", "W9", "W-8BEN", "W8BEN"}) and not (forms & {"W-4", "W4"})


def training_modules(cfg, hire_type_key=None):
    """The module list for a track: the track's own override if it has one, else the
    office-wide list. This is what lets a contractor get the invoicing module while an
    employee gets the timesheet one, without maintaining two configs."""
    default = cfg.get("training", {}).get("modules", [])
    if not hire_type_key:
        return list(default)
    ht = cfg.get("hire_types", {}).get(hire_type_key, {})
    return list(ht.get("training_modules") or default)


def substitutions(cfg):
    """The {{placeholders}} available in agreements, training content, and web pages."""
    o, p = cfg.get("office", {}), cfg.get("people", {})
    return {
        "office_name": o.get("name", ""),
        "office_short_name": o.get("short_name") or o.get("name", ""),
        "role_title": o.get("role_title", ""),
        "city_state": o.get("city_state", ""),
        "state": o.get("state", ""),
        "website": o.get("website", ""),
        "reply_to": o.get("reply_to") or p.get("owner", {}).get("email", ""),
        "emoji": o.get("emoji", "🏠"),
        "brand_color": o.get("brand_color", "#2f4a6d"),
        "brand_color_dark": o.get("brand_color_dark", "#22374f"),
        "owner_name": p.get("owner", {}).get("name", ""),
        "owner_email": p.get("owner", {}).get("email", ""),
        "owner_phone": p.get("owner", {}).get("phone", ""),
        "owner_title": p.get("owner", {}).get("title", ""),
        "supervisor_name": p.get("supervisor", {}).get("name", "") or p.get("owner", {}).get("name", ""),
        "bookkeeper_name": p.get("bookkeeper", {}).get("name", ""),
        "governing_state": cfg.get("legal", {}).get("governing_state", o.get("state", "")),
        # payroll / time reporting (module 06, W-2 track)
        "pay_cadence": cfg.get("payroll", {}).get("cadence", ""),
        "time_deadline": cfg.get("payroll", {}).get("deadline", ""),
        "time_method": cfg.get("payroll", {}).get("submit_method", ""),
        "pay_lag": cfg.get("payroll", {}).get("pay_lag", ""),
        # invoicing (contractor track). Falls back to the payroll values so an office that
        # never fills in payroll.contractor still gets a document without holes in it —
        # but the fallback text was written for employees, so it will read wrong to a
        # contractor. `python3 -m onboarding.config` says so out loud.
        **_contractor_pay(cfg),
        "example_pressure_value": cfg.get("training", {}).get("example_value", "$415,000"),
        "year": __import__("datetime").date.today().strftime("%Y"),
    }


_PLACEHOLDER = re.compile(r"\{\{\s*([a-z_]+)\s*\}\}")


def fill(text, cfg, extra=None):
    """Replace {{placeholders}} with config values. Unknown ones are left visible on
    purpose — a literal {{foo}} in an output document is a loud, findable bug, whereas
    silently blanking it would ship a contract with a hole in it."""
    subs = substitutions(cfg)
    if extra:
        subs.update({k: ("" if v is None else str(v)) for k, v in extra.items()})
    return _PLACEHOLDER.sub(lambda m: subs.get(m.group(1), m.group(0)), text)


def unresolved(text):
    """Any {{placeholder}} left in a finished document — callers should refuse to send."""
    return sorted(set(_PLACEHOLDER.findall(text)))


if __name__ == "__main__":
    # `python3 -m onboarding.config` = a config check you can run any time
    try:
        cfg = load()
    except ConfigError as e:
        print(f"\n{e}\n"); sys.exit(1)
    print(f"Config OK — {cfg['office']['name']}")
    for key, ht in enabled_hire_types(cfg).items():
        kind = "1099" if is_contractor(ht) else "W-2"
        print(f"  hire type  : {key} ({kind}) — {', '.join(ht.get('tax_forms', [])) or 'no forms'}"
              f", {len(training_modules(cfg, key))} modules")
    if not enabled_hire_types(cfg):
        print("  hire types : none")
    print(f"  storage    : {cfg['storage']['mode']}")
    print(f"  email      : {cfg['email']['mode']}")
    if contractor_pay_is_default(cfg):
        print("\n  NOTE: you have a contractor track enabled but payroll.contractor is empty, so\n"
              "        contractors will be shown your employee timesheet wording ('submit your\n"
              "        hours'). Fill in payroll.contractor in config/office.json with how you\n"
              "        actually want invoices sent.")
    if not cfg.get("legal", {}).get("reviewed_by_attorney"):
        print("\n  NOTE: legal.reviewed_by_attorney is false — the agreement templates are "
              "starting points,\n        not legal advice. Have your attorney read yours "
              "before a real person signs it.")
