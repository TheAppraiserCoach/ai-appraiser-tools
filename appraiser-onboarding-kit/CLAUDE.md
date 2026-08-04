# For Claude Code (or any AI assistant) working in this repo

If an appraiser has pointed you at this folder, they want one of two things: help setting
it up for their office, or help running it for a new hire. Read this first, then
[SETUP.md](SETUP.md).

## What this is

A self-contained onboarding system for a small appraisal office. Python 3 standard library
only — no packages, no build step, no database. Records are files on the owner's machine.

## The one rule about office-specific values

**Everything office-specific lives in `config/office.json`.** Name, people, hire types,
training module lists, payroll and invoicing wording, storage, email, legal state.

If you are about to edit a `.py` or `.html` file to change an office name, a person's
email, a pay schedule, or which forms someone gets — stop. That value belongs in the
config, and if it isn't reachable from there, that is a bug worth fixing properly rather
than hardcoding around.

Content a hire reads is markdown in `content/` and is meant to be edited freely.

## Helping with setup

Work through SETUP.md with them, in order. Do not skip ahead — a half-configured system
that reaches a real hire is worse than one that isn't running yet.

Three places to slow down and ask rather than assume:

1. **W-2 or 1099.** Do not pick this for them, and do not let a config choice quietly
   decide it. If they describe setting someone's hours and directing how the work is done,
   say plainly that this sounds like an employee regardless of what the paper says, and
   that their accountant should confirm before they send a contractor agreement.
2. **The agreements.** They are templates, not legal advice, and no attorney has reviewed
   them. Never tell an appraiser their agreement is ready to sign. Point them at the
   `[CONFIRM]` sections and tell them to have their own attorney read it.
3. **Module 05, the office workflow.** It ships with an example. If they don't replace it,
   their hires get trained on someone else's process. This is the single highest-value
   thing they can spend an hour on.

## Helping run it

Starting a hire:

```bash
python3 -m onboarding.send_welcome \
    --first Jane --last Doe --email jane@example.com \
    --start 2026-08-17 --pay "$22/hour" --type employee
```

`--type` takes plain words: `employee`, `contractor`, `foreign`. Leave it off and, if more
than one track is on, the command asks. In a script or a cron job it refuses instead of
guessing — never guess someone's tax classification.

Other commands:

- `python3 -m onboarding.config` — validate the configuration, see what's on
- `python3 -m onboarding.test_email` — prove mail works before a hire waits on it
- `python3 -m onboarding.compile` — rebuild the courses from content (the server does this
  itself at startup)
- `python3 -m onboarding.server` — run it

## Things this codebase deliberately does, so don't "simplify" them away

- **A 200 means filed.** Every POST that claims success has actually written the record.
  Nothing returns OK and hopes.
- **Never send a document with a hole in it.** If a `{{placeholder}}` doesn't resolve, the
  send is refused rather than mailing someone a letter with `{{owner_phone}}` in it.
- **Never report a send that didn't happen.** `mailer.send()` returns whether the message
  was handed off; callers surface a failure and print the link instead of exiting 0.
- **Progress is server-side, keyed by email.** A hire who switches from phone to laptop
  resumes instead of restarting.
- **Owner notes (`>` lines) and `[CONFIRM]` markers are stripped** before anything reaches
  a hire. Author-facing text must never appear in a signed document.
- **Errors are written for an office owner, not a developer.** A stack trace is a bug in
  the error handling.

## Data that must never end up in git

`config/office.json`, `records/`, any PDF, the compiled `web/content*.json` (it contains
the office's name, email, and phone), `progress.json`, and logs. All are gitignored — check
`git status` before committing anything and keep it that way.

A hire's folder contains their signed agreement and their tax forms. W-4s and W-9s carry
Social Security numbers. Treat that folder accordingly, and never paste its contents into a
chat window — including yours.
