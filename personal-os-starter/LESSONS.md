# Lessons — what goes wrong once this is running

Everything here was learned the hard way on a live system. Read it before you conclude
your setup is broken.

---

## 1. Uploaded files are a photograph, not a window

The single most common "it's broken" moment.

If you **uploaded** files to a project, GPT, or Gem, the model reads a copy made at upload
time. Edit the file and the model still sees the old version — and it will tell you a note
isn't there when it plainly is. Worse, **it also remembers things you deleted.** A copy
doesn't just go stale; it keeps what you removed.

Only a **live connection** (option 3 in `SETUP.md`) reads the current file.

*This was demonstrated live, by accident, in front of a room: the same question, the same
minute — the live connection answered correctly, the uploaded copy said "no record."*

**How to tell which you have:** write a nonsense phrase into a file, then ask about it. If
it knows, you're live. If not, you're cached, and you'll need to re-upload after edits.

---

## 2. Write your files the way you'll ask about them

A note that says *"my wife and I prefer bark in the garden beds"* will not be found by
someone asking *"what does [her name] prefer?"* — the name isn't in the file.

The file was right. The question didn't match its words. This is the most common reason a
second brain *feels* useless when it's actually fine.

**Use the names, nicknames, and phrasing you actually say out loud.**

---

## 3. Saved is not the same as visible

Three separate steps, and people conflate them:

1. **Saved** — the file on disk changed.
2. **Synced** — the cloud copy caught up.
3. **Indexed** — the model's copy caught up.

A change can be saved and still invisible. When something seems missing, check them in
that order rather than assuming the write failed.

---

## 4. Prune, or retrieval gets expensive

Rough token cost, measured on a real brain:

| Action | Tokens |
|---|---|
| A normal question (model searches) | ~1,000–2,000 |
| Writing a note | ~200 |
| Reading one whole big file | ~40,000 |

On a $20 subscription that isn't money — it's **room in the conversation**. Load 74,000
tokens of brain and the chat starts forgetting itself.

Two habits keep it cheap: **ask specific questions** (specific questions trigger a search,
vague ones trigger a full read), and **archive what's done.** The file that costs the most
is always the one nobody ever cleans out.

---

## 5. Capture-only systems nag you about things you've finished

If your brain only ever *appends*, it will keep surfacing a task you completed last week,
because nothing ever compared "I want to buy X" against "I bought X."

Build in a **retirement pass**: once a week, ask your AI *"what in here is already done or
no longer relevant?"* and archive it. Without this, people abandon the system within a
month — not because it forgot things, but because it nagged them.

---

## 6. Decide what never goes in

Anything in these files can surface in an answer, on a shared screen, or in front of a
class. Before you fill them out, decide what's off-limits.

Reasonable defaults:

- **No passwords or account numbers.** Those belong in a password manager.
- **No client or patient names** if you're in a licensed profession.
- **Medical specifics:** keep the useful part, drop the identifying part. "5 mg of my
  peptide, every 4 days" is useful. The drug name adds nothing and is the part you'd
  regret reading aloud.
- **Use codenames for sensitive third parties.** A real firm name got read off a screen in
  front of a room once. Once is enough.

Write your rules directly into `CLAUDE.md` so every model follows them without being
reminded.

---

## 7. Connectors break. The files don't.

Integrations fail — a connector loses auth, a permission changes, an upload goes stale.
That's the tools, not your system.

This is the whole point: **your brain is a folder of text.** When a connector breaks you
lose access for an afternoon. You never lose the brain. Rent the model, own the files.
