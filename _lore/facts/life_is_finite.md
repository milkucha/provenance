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

**The number.** A character's lifespan is recorded in `_maps/npcs/lifespans.json` — deliberately
*not* in their registry entry, because that entry is what `/enact` loads in order to play them, and a
span sitting there would put the number in their own context at exactly the moment it must not be.
The enactment asks `scripts/horizon.py` instead, which answers with a coarse band (`early`,
`established`, `late`, `final`) and never the figure. So the number is never revealed to them — not
as a count, not as a countdown, not as a hint that they are "running low." They live the way people
actually live: certain of the end, ignorant of the date.

The single exception is the last one. When a character enters what turns out to be their final
encounter, they know it is the final one, and they play it knowing. That knowledge arrives with the
scene itself and never one scene early.

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
