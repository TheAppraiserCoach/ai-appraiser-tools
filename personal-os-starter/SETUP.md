# Setup — getting your AI connected to these files

There are three ways, from easiest to most powerful. **Start with option 1.** Most people
never need option 3.

---

## Option 1 — Upload the files (5 minutes, works everywhere)

Attach the markdown files directly to a project or custom assistant.

- **Claude:** create a Project, upload the files to Project Knowledge.
- **ChatGPT:** create a Custom GPT (or a Project), upload the files.
- **Gemini:** create a Gem, add the files under Knowledge.

**Works immediately. No accounts, no servers, no technical skill.**

**The catch, and it matters:** the model reads a **copy** made when you uploaded. Edit the
file afterward and the model will not see the change until you re-upload. It will
confidently tell you something isn't there when it is. See `LESSONS.md`, lesson 1.

Best for: reference material that doesn't change daily — your voice, your processes, your
principles.

---

## Option 2 — Cloud folder (10 minutes, good middle ground)

Put the folder in Google Drive, Dropbox, or OneDrive, and connect that to your AI.

- Edit files on your computer or phone; they sync to the cloud.
- Some AI integrations read the file live; some index a copy. **Test yours** — write a
  nonsense word into a file, then ask about it. If it knows, you're live. If not, you're
  cached.

Best for: a working setup you'll actually update, without running anything technical.

---

## Option 3 — Live connection (MCP) (advanced, requires a server)

Run a small MCP server over the folder and connect Claude/ChatGPT to it. The model reads
your file **at the moment you ask**, so a note written seconds ago is available instantly.
It can also **write back** — logging notes to your journal from any chat.

This is what makes "tell Claude something, ask ChatGPT about it ten seconds later" work.

**Be honest about the cost:** you need somewhere to run it (a small VPS or an
always-on machine), and you need to handle authentication. Do not put a no-auth URL on the
public internet with your personal files behind it unless you understand that anyone with
that link has everything.

Best for: people who want live, two-way memory and are comfortable running a server — or
who have someone who can set it up for them.

---

## Version control (recommended regardless of option)

Put the folder in a **private** GitHub repo. You get free history of every change and the
ability to undo anything. Ten minutes to set up, and it's the difference between "I think I
deleted something" and "here it is."

---

## Testing that it worked

Ask your AI:

> "Based on my files, what do you know about my business, and what are my current
> priorities?"

If it answers from your files, you're connected. If it hedges or asks you to paste
something, it isn't reading them — check that the files actually attached, and that you're
in the project/gem/assistant you set up rather than a plain chat.
