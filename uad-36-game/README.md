# UAD 3.6 — Ultimate Appraiser Defender

A free browser game from The Appraiser Coach. You're the appraiser. Laser the corners, grab the required photos, write your notes, and get back to the car before the dog, the goat, the chickens, the Realtor and the homeowner eat your hour.

**Play it:** https://game.dustinharrisos.com/ (or the copy in this folder — open `index.html`, it works on a phone or a laptop, no install).

## What's in here

- `index.html` — the whole game. One file, plain JavaScript, emoji art, no libraries, no build step. All the tuning knobs (clock speed, laser charges, dog speed, how long a stun lasts) are in the `CFG` object at the top.
- `how.html` — the "how this was built" page.
- `server.py` — optional. A tiny Python server that serves the folder and accepts the email-gate submissions (`POST /api/lead`) into a local file. You only need it if you turn the email gate on (`gateAfterRounds` in `CFG`). The game runs fine without it.

## How it was built

Dustin described the game out loud in an airport, in plain English, and an AI assistant (Claude Code) built the first playable version before he landed. Every change after that came from playing it on a phone and saying what was confusing. Total: one evening of attention. No programming background required.

Fork it, change the pests, add your own property types. The three properties live in the `PROPS` array — copy one and edit.

## License

Same as the rest of this repo. Not affiliated with any software vendor; "UAD 3.6" here is a joke about the appraisal form, not the standard.
