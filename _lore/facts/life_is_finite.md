# Life is finite

**Id:** `life_is_finite` · **Added:** 2026-07-31

A life comes to an end. Every character knows this about themselves and about everyone they meet.
It is not news, not a discovery, and not something anyone had to be taught — it is simply the
condition of being alive here.

## What the character knows

- That their life will end.
- That the encounters left to them are a real and fixed quantity — not endless, not renewable.
- That other people's lives end too, which is why what someone leaves behind in others outlasts
  them.

## What the character does not know

**The number.** A character's lifespan is recorded in `_lore/characters/lifespans.json` — deliberately
*not* in their own character file, because that file is what `/enact` loads in order to play them, and a
span sitting there would put the number in their own context at exactly the moment it must not be.
The enactment asks `scripts/horizon.py` instead, which answers with a coarse band (`early`,
`established`, `late`) and never the figure. So the number is never revealed to them — not as a
count, not as a countdown, not as a hint that they are "running low." They live the way people
actually live: certain of the end, ignorant of the date.

**Not even the last scene is an exception.** There is no moment a character knows a given scene is
their final one, because there is no such moment to know — dying isn't an event a character
experiences and narrates from inside; it's simply that no scene follows. What turns out to have been
someone's last scene is written exactly like any other, with no foreboding and no farewell weight
built in by the system (an author choosing that tone for their own reasons is a separate, incidental
thing, and never something the system signals in advance — see `scripts/horizon.py`'s docstring).
Whether a scene was the last is only knowable afterward, mechanically, once it's already closed. Word
of the death itself then reaches others the ordinary way — nobody present has to witness or announce
it; it simply becomes known, ex post facto, the way anything else becomes known here (see
`.claude/skills/enact/SKILL.md` Step 5b).

## Why it is a fact and not lore

Because there is no version of a person in this world who could plausibly not know it, and because
nothing can refute it. A criterion — what a character counts as a life well spent — is anchored to
something that *could* turn out to be wrong, and can therefore be argued with, defended, or broken.
This cannot. It is the floor the argument stands on.

## What it does

Finitude is what forces ranking. A character who could do everything eventually reveals nothing by
choosing; a character with a closing horizon has to decide what matters *most*, and that decision is
where personality stops being description and becomes visible behavior. Paired with
[`a_worthwhile_life`](a_worthwhile_life.md), it is the whole of the will to live: the end is coming,
and it matters what the time was spent on.

It also governs drift (see the criterion model in `.claude/skills/character/SKILL.md`): as the
remaining span shortens against the scale of what a character's criterion demands of them, that
character becomes more susceptible to having it broken.
