> 👉 **Just want the overview?** [Open the Onboarding Kit page](https://theappraisercoach.github.io/ai-appraiser-tools/appraiser-onboarding-kit/). **Heads up:** this tool is a small program that runs on your own computer. To get the files, go to the [main repo page](https://github.com/TheAppraiserCoach/ai-appraiser-tools), click the green **<> Code** button, then **Download ZIP**. [← Back to all tools](https://theappraisercoach.github.io/ai-appraiser-tools/)

# Appraiser Office Onboarding Kit

Onboard a new person into an appraisal office with one command.

You type their name, email, start date, pay, and whether they are an employee or a
contractor. They get an email with a link. Behind that link is everything: the training
with quizzes, the agreement to e-sign, the tax forms to upload. You get the finished
paperwork filed and a note when they're done.

```
python3 -m onboarding.send_welcome \
    --first Jane --last Doe --email jane@example.com \
    --start 2026-08-17 --pay "$22/hour" --type employee
```

Leave off `--type` and it asks. Say `employee` or `contractor` — you never have to
remember a config key.

## What the new hire gets

One link, personal to them. No account to create, nothing to retype. They can start on
their phone in the driveway and finish on a laptop that night — progress is keyed to their
email address, so switching devices resumes instead of restarting.

1. **Training** — six short modules, each ending in a quiz they have to pass:
   welcome and role, USPAP and ethics, confidentiality and data, independence and pressure,
   how work moves through the office, and getting paid. They earn a completion certificate.
2. **Their agreement** — read and e-signed in the browser, with a timestamp and IP on the
   executed copy.
3. **Tax paperwork** — the right forms for their track, uploaded signed.

## Two tracks, because two kinds of hire

| | W-2 Employee | 1099 Contractor |
|---|---|---|
| Agreement | Employment Agreement | Independent Contractor Agreement |
| Tax forms | W-4 + I-9 (in-person ID check) | W-9 (W-8BEN if not a US person) |
| "Getting paid" module | Timesheets, overtime, never off the clock | Invoicing, self-employment tax, your own expenses |

The track is chosen per hire, so an office that uses both never has to maintain two setups.
This matters beyond convenience: handing a 1099 contractor training that tells them to
submit hours and never work off the clock contradicts the agreement they just signed, and
reads as evidence they were really an employee.

**Classification is your call and your risk.** Signing a paper that says "independent
contractor" does not make someone a contractor — the IRS and your state look at who
controls the work. The owner's note at the top of the contractor agreement covers this. If
it's close, ask your accountant before you send it.

## Everything office-specific lives in one file

`config/office.json` holds your office name, your people, your training content choices,
your payroll and invoicing wording, where records are filed, and how email is sent. No
Python or HTML file in this repo contains your office name. If you find yourself editing
code to change a name, that's a bug in the kit.

`config/office.json` is gitignored. So are `records/`, every PDF, and the compiled course.
Your hires' tax forms and signed agreements never go near git.

## Getting started

See **[SETUP.md](SETUP.md)** — about twenty minutes, most of it deciding what your office
actually does. If you use Claude Code, point it at this repo and it will walk the setup
with you; see [CLAUDE.md](CLAUDE.md).

Requires Python 3.8+. No packages to install. Chrome or Chromium, if present, is used to
render PDFs; without it the kit saves styled HTML records instead of crashing.

## The legal templates are starting points

The agreement templates were written for a small US residential appraisal office. They are
**not legal advice**, no attorney has reviewed them, and no one connected with this kit is
your lawyer. Sections marked `[CONFIRM]` are the state-sensitive ones. Have your attorney
read whichever agreement you use before a real person signs it.

The training content is about professional standards — USPAP, independence, fair housing,
confidentiality. It does not replace state-required trainee supervision, and module 5 is
written to be replaced with your office's actual workflow.
