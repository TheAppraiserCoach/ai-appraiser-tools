# How an Appraiser Built a Video Game in One Evening — A Dustin OS White Paper

> **Read the designed version:** https://theappraisercoach.github.io/ai-appraiser-tools/how-we-built-a-game-whitepaper/  
> **PDF:** https://theappraisercoach.github.io/ai-appraiser-tools/dist/How-An-Appraiser-Built-A-Video-Game-Whitepaper.pdf  
> This README is the same paper in plain Markdown so it reads here on GitHub.

Published by The Appraiser Coach, October 2026. Educational reference. The game itself is free to play at [game.dustinharrisos.com](https://game.dustinharrisos.com/), and its source is in this same repository.

> ### Read this first
>
> - **This is a story about a process, not a programming tutorial.** You will not learn JavaScript here. You will learn what it feels like to have something built for you by describing it.
> - **"UAD 3.6" in the title is a joke about the appraisal form.** The game is not affiliated with any software vendor, Fannie Mae, Freddie Mac, or the UAD standard.
> - **No warranty, no tech support.** The code is published in this repository for anyone who wants to change the pests. If you break it, you get to keep both pieces.

> ### Contents
>
> 1. [The idea, in the exact words it was given](https://theappraisercoach.github.io/ai-appraiser-tools/how-we-built-a-game-whitepaper/#idea)
> 2. [What the AI decided without being told](https://theappraisercoach.github.io/ai-appraiser-tools/how-we-built-a-game-whitepaper/#decisions)
> 3. [Nine rounds of "that's confusing" — the actual log](https://theappraisercoach.github.io/ai-appraiser-tools/how-we-built-a-game-whitepaper/#loop)
> 4. [How it got tested with nobody playing it](https://theappraisercoach.github.io/ai-appraiser-tools/how-we-built-a-game-whitepaper/#testing)
> 5. [What's actually under the hood](https://theappraisercoach.github.io/ai-appraiser-tools/how-we-built-a-game-whitepaper/#hood)
> 6. [The email question, and how the answer changed three times](https://theappraisercoach.github.io/ai-appraiser-tools/how-we-built-a-game-whitepaper/#email)
> 7. [What it cost](https://theappraisercoach.github.io/ai-appraiser-tools/how-we-built-a-game-whitepaper/#cost)
> 8. [Why this matters for appraisal tools](https://theappraisercoach.github.io/ai-appraiser-tools/how-we-built-a-game-whitepaper/#appraisal)
> 9. [If you want to try this yourself](https://theappraisercoach.github.io/ai-appraiser-tools/how-we-built-a-game-whitepaper/#tryit)

## 1. The idea, in the exact words it was given

On the morning of October 4, 2026, Dustin Harris was sitting in the airport at Rome Fiumicino at the end of a two-week trip, triaging his to-do list with the AI assistant that runs his businesses. One of the items on that list had been sitting there since late September. It read, verbatim:

> Create an Appraiser based video game surrounding the Appraisal inspection where you have to fight off homeowners and Realtors and measure the house while a dog is trying to bite you etc. Make it browser based and fun with progressions and something that is shareable. *— the second-brain entry, as captured from a voice note*

That is the entire specification. There was no design document. When the assistant asked what "measure the house" should mean in a game, Dustin answered the way an appraiser would: a laser and a tablet for the exterior, photos inside and out, notes on what you see, and you have to survive the Realtor, the dogs, the goats, the chickens, the homeowner and the neighbors. Winning meant surviving all of it in under thirty minutes, with the minutes ticking like seconds. Then levels get harder: tougher houses, more obstacles, new property types.

The assistant laid out a plan that would fit a time budget — one level first, in a scratch folder, nothing shipped until he had played it and said it was fun — and asked for a go. The reply was three words:

> Build a prototype.

The first playable version was on his phone before the connecting flight out of Amsterdam.

## 2. What the AI decided without being told

This is the part most people underestimate. A short spec only works if the thing on the other end makes a few hundred small decisions well, and makes the big ones in a way you can undo. Here is what got decided on the assistant's own judgment, before any feedback:

- **One file.** The whole game is a single HTML page, around 600 lines, no libraries, no build step, no framework. If it works on a phone's browser it works everywhere, and there is nothing to install or update.
- **Emoji as art.** The appraiser is 🕵️, the dog is 🐕, the realtor is 🧑‍💼. Every phone already has these drawn beautifully. No artist, no image files, no licensing.
- **Top-down view, one screen per property.** You can see the whole lot, so the game is about routing and timing rather than exploring.
- **Hazards as "interruptions," not enemies.** Nothing has hit points. Bumping into the Realtor costs you three minutes and a line of dialogue. That turned out to matter later.
- **All the "feel" numbers in one place.** Clock speed, dog speed, laser charges, how long a stun lasts — every one of them is a named knob at the top of the file. When Dustin later said "double the time," it was a one-number change.
- **A scratch folder and a private link.** Not the public tools repository. Nothing goes out until the person who asked for it has played it.

Two of those — the single file and the knobs — are the reason the next section was possible at all.

## 3. Nine rounds of "that's confusing" — the actual log

What follows is the real sequence of feedback, pulled from the conversation. Dustin was traveling the whole time: airport, two flights, a layover, then home. He never saw code. Each row is one message from him and what shipped in response. Times are approximate minutes from his message to the fix being live on the link.

| What Dustin said | What changed | Time |
|---|---|---|
| "It should be named UAD 3.6 but UAD should stand for Ultimate Appraiser… not sure what to do with the D. Also the appraiser should be able to use his laser measure as a weapon." | Renamed *Ultimate Appraiser Defender*. The laser now fires: a red beam, three charges that recharge. | ~10 min |
| "How can we make this mobile friendly?" | Full-screen canvas, a camera that follows you zoomed in on phones, portrait support, on-screen buttons. | ~25 min |
| "I can't move. It is not clear how to move. Whatever gets zapped should die and go away for a period of time." | The hidden joystick was replaced with tap-where-you-want-to-walk and a pulsing "👆 Tap where you want to walk" prompt. Zapped pests vanish. | ~15 min |
| "Still says time on clock is 30. How do I fire the laser to measure and to shoot obstacles?" | One-hour clock. The action button now labels itself — 📐 MEASURE, 📸 PHOTO, 📝 NOTE — and the ⚡ ZAP button auto-aims at the nearest pest. The test harness also found the Realtor spawning on top of the player and interrupting every tap; he was moved and a three-second grace period added. | ~30 min |
| "I got done with the game and went back to the car and did not know how to leave and so I lost." | A steering wheel bobs over the car when everything's done, a banner says where to go, an arrow points at the car if it's off-screen, and walking onto it drives away automatically. | ~12 min |
| "Instead of killing the obstacles, let's stun them so they're frozen and move away. Also there needs to be a place on the main screen that goes to how it was built. Also, why is it connected to the exam site? Can't it be its own game.dustinharrisos.com?" | Zaps now knock the pest back and freeze it in a bubble for twenty game-minutes; nothing dies. A "how this game was built" page. Its own domain. | ~35 min |
| "On the main page it should show that one second equals one minute." | Declined as written — the clock actually runs two real seconds per minute, and he had just called that pace perfect. The screen says the true number. He agreed. | — |
| "Look at this as if you're a brand new person who has never seen what I do before, and improve the game so it's even more impressive." | A real title screen with the pests wandering behind it. Assignment cards ("NEW ORDER — 412 Maple St, 3 bed / 1 bath, lender needs it today"). Three property types: Rambler, Farmhouse (two dogs, two goats, a cow), Condo (HOA president, cat, tenant). Sound effects, screen shake, score pops, random one-liners. Ranks from Trainee to Review Appraiser Legend. A share button. | ~90 min |
| "I keep taking a picture of the front or the street and then I go around the house and find out the picture has not been taken again." | Diagnosed: the goat was eating a random finished photo on contact, and the notice was easy to miss. Mechanic removed. Street spot moved down the block. Also added a 🏠 home button he'd asked for. | ~10 min |

Notice what is not in that table: a single line of code, a single technical term from Dustin, a single "can you send me a screenshot of the error." Every message is a player describing what confused him. That is the whole method.

> **The one time the assistant said no** is worth a second look. "Say one second equals one minute" was a reasonable-sounding request that would have put a false number on the screen. Pushing back cost one sentence and kept the thing honest. An assistant that does everything you say, including the wrong things, is not actually saving you work.

## 4. How it got tested with nobody playing it

Dustin was on a plane for most of this. So who played the game between his messages? Nobody — and the game still got tested every round, three ways:

1. **A scripted player.** The assistant wrote a small robot that opens the game in an invisible browser, walks a fixed route through the whole house, measures, photographs, zaps anything close, and reports whether it won and in how many minutes. That robot caught the first balance problem (the original clock was unwinnable: the bot finished every task and died at the car) and the first level-design bug (a back door 32 pixels wide for a 26-pixel player, which the robot got wedged in). It ran after every change. If it stopped winning, something had broken.
2. **A reachability check.** When three property types were added, the assistant ran a flood-fill from the starting point over every property and confirmed every corner, photo spot, note and the car could physically be reached. The Condo failed on the first try — its front door opened straight into an interior wall — and was fixed before Dustin ever saw it.
3. **Phone screenshots.** The invisible browser was told to pretend to be an iPhone in portrait and landscape, tap the buttons, and take pictures. The assistant looked at the pictures. That is how it noticed the player sprite was unreadable on dark asphalt (fixed with a yellow ring), that the fire button sat exactly on the starting position, and that the hint bar was covering the player. The server didn't even have an emoji font; one got installed just so the screenshots would show what a phone shows.

None of this is exotic. It is the kind of checking a careful developer would do, done automatically, in the minutes between one message and the next. It is also why the feedback loop in section 3 stayed about *fun* rather than about *bugs*.

## 5. What's actually under the hood

For the curious, and so nobody thinks there is a trick:

- **The game** is one HTML file. Drawing is done on a canvas; the house, the yard, the pests and the appraiser are all drawn fresh sixty times a second. Each property is a small list: where the walls are (with door gaps), where the rooms are, where the photo spots and notes sit, and which pests live there with what speed and what lines they say. Adding a fourth property means copying one of those lists.
- **Movement** on a phone is tap-to-walk: you tap a spot, the appraiser walks there, sliding along walls. On a keyboard it's the arrow keys.
- **The pests** have three brains: chase (if you're in their zone and within range, come at you), patrol (walk the fence line), wander (chickens). The homeowner lives inside the house and never leaves; the dog lives outside and never comes in.
- **The laser** auto-aims at the nearest pest in range, draws a beam, and if it connects the pest slides away and freezes for twenty game-minutes.
- **Sound** is synthesized on the fly — a handful of beeps and sweeps — so there are no audio files to load.
- **Hosting:** on Dustin's own server behind a Cloudflare tunnel at game.dustinharrisos.com, and a static copy on GitHub Pages in this repository. A forty-line Python script serves the folder and accepts the optional email form into a local file. No database, no third-party service, no analytics.
- **Your personal best** is stored in your own browser. Nothing about play is sent anywhere unless you type your email into the optional box.

## 6. The email question, and how the answer changed three times

The first plan was an email gate: a wall before play. In the first conversation about it the assistant suggested the wall come *after* the first round instead, so the player has a reason to want more. Dustin agreed, then while it was being built moved it to after the second round, then switched the gate off while his members tried it. The next morning he reframed it: not a gate, an invitation. "Would you like to know more about how to create real appraisal tools with AI?" Optional, once, with a "no thanks, keep playing" button.

That is the right answer, and it took three wrong ones to get there. The point of writing it down is that every version was a one-knob change. The cost of being wrong was fifteen minutes, so it was fine to be wrong a few times.

## 7. What it cost

- **Dustin's attention:** roughly three hours total, in five-to-ten-minute slices across an airport, two flights and the next morning. Almost all of it was playing the game and typing one paragraph.
- **Money:** nothing beyond the AI subscription and a server he already runs. Domain, hosting, GitHub: zero marginal cost.
- **Code written by a human:** none.

## 8. Why this matters for appraisal tools

A game is a deliberately silly thing to build. That is why it is a good demonstration: nobody can claim it only worked because the AI had seen a thousand examples of exactly this. Replace "laser the corners" with "check every UAD field against the engagement letter" and the loop is identical:

1. Describe the thing in the words you'd use with a colleague.
2. Ask for a prototype under a time budget, in a scratch folder, nothing shipped.
3. Use it. Say what's confusing. Say what's wrong. Say what you changed your mind about.
4. Let the assistant test between your messages so your feedback stays about the *work*, not about bugs.
5. Publish when it's useful, not when it's perfect. Then keep going.

Every tool in this repository — the QC reviewer, the engagement-letter parser, the depreciated cost calculator — was built this way. The game just makes the method visible, because the gap between "an appraiser in an airport" and "a working video game on his phone" is too wide to explain any other way.

## 9. If you want to try this yourself

You don't need this game's code, though it's here if you want it. You need an AI assistant that can write and run code on a computer you control (at the time of writing Dustin uses Claude Code), a folder, and a thing you've wanted for years and never had time to build. Start smaller than a game. A checklist that becomes a scorecard. A letter you rewrite every week. Describe it, ask for a prototype, play with it, and type what's confusing.

If you'd rather see it done step by step, with appraisal tools instead of goats, that's what the [Appraiser AI Academy](https://theappraisercoach.com/products/) is for.

> ### Repeat of the disclaimer
>
> - Educational reference. The game and this paper are provided as-is, with no warranty and no support.
> - "UAD 3.6" is used here as a joke about the appraisal form. No affiliation with any vendor or GSE is implied.
> - Quotes from Dustin are his own words from the build conversation, lightly trimmed for length.

---

*Published by [The Appraiser Coach](https://www.theappraisercoach.com). Play the game: [game.dustinharrisos.com](https://game.dustinharrisos.com/). Educational reference. No warranty, no tech support. Source for the game and this site is on [GitHub](https://github.com/TheAppraiserCoach/ai-appraiser-tools).*
