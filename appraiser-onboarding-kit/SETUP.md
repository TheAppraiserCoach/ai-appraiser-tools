# Setup — about twenty minutes

Most of this is deciding what your office actually does. The software part is short.

You need Python 3.8 or newer. Check with `python3 --version`. Mac and Linux have it. On
Windows, install it from python.org or use WSL.

---

## 1. Get the files and make your config

```bash
cd office-onboarding-kit
cp config/office.example.json config/office.json
```

`config/office.json` is **yours**. It is gitignored and never leaves your machine. Open it
in any text editor. Every value in it is explained in a `_comment` next to it.

Fill in, at minimum:

- `office.name`, `office.short_name`, `office.city_state`, `office.state`
- `office.role_title` — the job title on the agreement, e.g. "Appraisal Trainee"
- `people.owner.name`, `.email`, `.phone`, `.title` — where completed paperwork goes
- `legal.governing_state`

Then check your work:

```bash
python3 -m onboarding.config
```

It either says `Config OK` and summarizes your setup, or tells you in plain English what
is wrong. Fix and re-run until it is clean. It won't let a half-configured system meet a
real hire.

---

## 2. Decide your hire types

In `hire_types`, turn on the tracks you use and turn off the rest:

- `w2_employee` — employees. W-4 and I-9, employment agreement, timesheet training.
- `contractor_1099` — independent contractors. W-9, contractor agreement, invoicing
  training.
- `contractor_foreign` — contractors outside the US. W-8BEN. Off by default.

If you turn on only one, you never have to say which track a hire is on. If you turn on
more than one, you say `--type employee` or `--type contractor` when you start someone —
or leave it off and the system asks.

**If you use contractors, fill in `payroll.contractor`** — how you want invoices sent, the
deadline, and when payment goes out. Leave it blank and contractors get shown your employee
timesheet wording, which contradicts the agreement they just signed. `python3 -m
onboarding.config` warns you about this.

> **Classification.** A signature on a contractor agreement does not make someone a
> contractor. If you set their schedule, tell them how to do the work, and they work only
> for you, the IRS and your state will likely call them an employee — and the bill for
> getting it wrong is back taxes, penalties, and unpaid overtime. Ask your accountant when
> it is close.

---

## 3. Make the content yours

Everything a hire reads is markdown in `content/`. Edit it like a document.

**Do this one first:** `content/training/05-office-workflow.md` describes how work moves
through the office, step by step. It ships with a detailed example workflow. Replace it
with yours — that is the module that makes this training about *your* office instead of
appraisal in general.

Also worth your time:

- `content/agreements/employment-agreement.md` and
  `content/agreements/independent-contractor-agreement.md` — read the owner's note at the
  top of each, then read the sections marked `[CONFIRM]`. Those are the state-sensitive
  ones. **Have your attorney read whichever one you use.** When they have, set
  `legal.reviewed_by_attorney` to true in your config.
- `content/training/06-getting-paid.md` (and the `-contractor` version) — the pay and
  invoicing mechanics come from your config, but read them once against how your office
  really works.
- `content/emails/welcome.md` — the email a new hire gets.

Owner's notes are lines starting with `>`. They are stripped before anything reaches a
hire, so you can leave yourself instructions in the file safely. So are the `[CONFIRM]`
markers.

Quiz answers are marked with a ✅ in the option. Any module you edit, re-check its quiz.

---

## 4. Wire up email

Until you do this, `email.mode` is `"none"` — the system prints each message for you to
copy and paste. That works, and for a one-person office it may be all you want.

To send for real, set in `config/office.json`:

```json
"email": {
  "mode": "smtp",
  "from_name": "Your Office Name",
  "smtp": {
    "host": "smtp.gmail.com",
    "port": 587,
    "username": "you@yourdomain.com",
    "password_env": "ONBOARDING_SMTP_PASSWORD"
  }
}
```

**The password never goes in the config file.** It goes in an environment variable, so it
can't be committed, backed up, or emailed by accident:

```bash
export ONBOARDING_SMTP_PASSWORD='your app password'
```

Put that line in your `~/.zshrc` or `~/.bashrc` so it survives a reboot.

**Gmail / Google Workspace:** your normal password will not work. Turn on 2-Step
Verification, then Google Account → Security → 2-Step Verification → App passwords, and
generate one for "Mail." It looks like `abcd efgh ijkl mnop` — paste it with the spaces
removed.

**Other providers:** host and port come from your provider's "SMTP settings" page. Port 587
with STARTTLS is the usual pair. Microsoft 365 is `smtp.office365.com:587`.

Then prove it works, before anyone is waiting on it:

```bash
python3 -m onboarding.test_email
```

It logs in, sends a real test message to your owner address, and tells you exactly what is
wrong if it fails. Do not onboard anyone until this passes.

---

## 5. Decide where records get filed

`storage.mode` is `"local"` by default: everything lands in `records/` in this folder, one
subfolder per hire, plus a `tracker.csv`. Nothing leaves your machine and there is nothing
to set up.

`records/` and every PDF are gitignored. Signed agreements, W-4s, and W-9s hold Social
Security numbers — keep that folder on an encrypted disk and in your normal business
backup, and don't put it in a shared cloud folder without thinking about who else can see
it.

(`"google"` mode files into a Drive folder and a tracker Sheet instead. It needs the `gog`
CLI configured with your Google account; if you aren't already using it, stay on local.)

---

## 6. Run it

```bash
python3 -m onboarding.server
```

Leave that running. It serves the hub, the course, the agreement, and the paperwork page on
`http://localhost:8620`, and it recompiles the training from your content every time it
starts — so edit content, restart, refresh.

In another terminal, start a fake hire and walk it yourself before a real person sees it:

```bash
python3 -m onboarding.send_welcome \
    --first Test --last Person --email you@yourdomain.com \
    --start 2026-09-01 --pay "$20/hour" --type employee
```

Open the link it prints. Take the quizzes, sign the agreement, upload anything as the tax
forms. Then look in `records/` and see what you'd actually have on file. Do it again with
`--type contractor` if you use contractors — it is a different agreement and a different
pay module, and you should read both.

Delete the test folder out of `records/` when you're done.

---

## 7. Letting a hire reach it from their phone

`localhost:8620` only works on your own machine. A new hire on their phone needs a public
address, and `server.public_url` is what goes into their welcome email.

The simplest option that doesn't mean running a server 24/7 is a Cloudflare quick tunnel:

```bash
cloudflared tunnel --url http://localhost:8620
```

It prints a public `https://something.trycloudflare.com` URL. Put that in
`server.public_url`, send the welcome, and leave both the server and the tunnel running
while the hire works through it. The URL changes every time you restart the tunnel, so
send the welcome email after you start it, not before.

If you already have a domain and a machine that stays on, point it at port 8620 instead and
set `public_url` once.

---

## When something breaks

- `python3 -m onboarding.config` — is the configuration sane?
- `python3 -m onboarding.test_email` — can this machine actually send mail?
- `server.log` — every request and every filing, with timestamps.
- A hire's progress is keyed to the email address you started them with. If they typed a
  different one, they'll look like a new person. Start them again with the address they
  actually use.
