# Cassius — design review of the doc, as built

Each system from the design doc, checked against the four project questions:
(1) worth designing this way? (2) better presentation? (3) logic holes? (4) a real roguelite decision, or an auto-pick?

## Changes I made, and why

**1. One grain pool instead of "food" and "tribute".**
The doc treats supplies and the Emperor's levy as separate. Separate pools mean neither ever hurts. In the build the grain your men eat *is* the grain the ledger wants (120 by the end, shown on the HUD beside the daily burn). Every recruit, every mercy and every lost day now visibly eats the quota. This is the single change that does most to make choices non-obvious.

**2. One currency, not gold + growth points.**
The doc gives "gold and growth rewards" after battle. Two currencies let the player max the tree for free. With denarii alone, a doctrine competes with ten measures of grain and with five recruits.

**3. Omens reveal fixed truth; they never roll dice.**
Hole in the doc: if the omen is generated when you sacrifice, it is a slot machine, and "an omen that only tells you something unavoidable" reads as a wasted item. Here the next battle (composition, hidden flank force, side, arrival time) is generated when the leg starts. The altar only uncovers parts of it, and the menu tells you beforehand how clear the omen will be (faint / clear / blazing). The "unavoidable" lines are real arithmetic: how short of quota you are on current pace, or that the forest already sent a third warband because of what you did.

**4. Every loot item has four exclusive uses.**
Sell (denarii), burn (omen), equip (some), or deliver (the ledger needs 3 offerings). Without the fourth use, "sacrifice your most valuable item" is always right. Regional altars double the value of what that people prize (north: oaths, west: growth, east: memory, south: wealth and lives), so *where* you burn something matters.

**5. The portrait.**
The doc's "sacrifice your men or your family's picture" only works if the picture has no mechanical value. It sells for 0, cannot be delivered, and gives the strongest omen available. The only cost is the ledger line.

**6. The march is 3D with a Hades camera (as the doc specifies).**
A first build used a Kingdom side view; that was reverted at the designer's request. The road is now a 3D corridor seen through a tilted orthographic camera and rendered at 480x270, so meshes come out as pixels ("3D model, then pixel art"). Props are low-poly primitives; characters are still billboarded pixel sprites until real models exist. The doc's open question - how does the scene extend? - is answered by making a leg a straight corridor of fixed length whose props are scattered from a seed, so any leg length is free. Time on the road is still tied to distance walked (the sun and shadows move as you advance), so reading a menu never costs food; days are charged at the crossroads.
Trade-offs to know: an orthographic top-down camera has no natural parallax, so the doc's "foreground / mid / background at different speeds" is gone, and so is Kingdom's mirrored river (the water is a flat shaded plane). Free movement currently adds feel but no decisions - everything interactable still sits along one line. If the Hades view is to earn its cost, legs need width that matters: side paths, things you can only reach by leaving the road, or stops you can walk around.

**7. Armour floor.**
The doc's formula `atk × bonuses × reduction − armour × bonuses` goes to zero or negative (archers vs testudo: 7 − 16). I kept the formula and added a floor of 15% of pre-armour damage. Without it, a testudo is literally invulnerable to arrows and the correct play is trivially "always testudo".

**8. Formation leash.**
"Ring" and "testudo" only mean something if men hold their place. Each formation has a leash distance from its slot (ring 4 px, line 26 px, loose 40 px). This is what makes tight formations hold and loose ones swarm.

**9. Limited levy per camp.**
Unlimited recruiting makes casualties a gold tax. Each camp has a small pool (22 in imperial land, 12 elsewhere).

**10. A toll instead of a forced fight.**
"How much wipe risk is this reward worth?" needs an alternative to fighting. You may always abandon half your grain to pass.

## Still weak — decide before building further

- **Shield infantry has five formations; two are redundant.** Wedge on a slow shield wall is never the right call. Suggest cutting shields to Line / Testudo / Ring.
- **"Ring can shelter another regiment"** is not implemented. It needs pathing rules (who may enter, do archers fire out?) and I suspect it becomes the dominant opening. Worth a paper test first.
- **Promotion snowball.** Kills → rank → +10% damage and armour makes your best regiment better, so you always feed it kills. Consider promotions that offer a *choice* of perk, or that raise upkeep.
- **Retreat is nearly free.** Resting regiments heal with no downside except time. Consider "resting regiments eat double tonight".
- **Route choice is thin.** Two cards, mostly flavour plus enemy type. It needs visible stakes per road (grain available, altar type, known enemy size) to be a decision.
- **Seven regiments × 35 on one screen** is readable but busy at 480×270. If you want Sword & Banner's scale, the battle needs a panning camera.
- **The ending's single choice does a lot of work.** It currently hinges on the horn. Seeds and codex promises should also be payable or breakable at the altar.

## Not built yet
Faction-specific mechanics beyond stats (curses are in; traps, illusions, boarding raids are not), elite regiments other than the Oathshields, weather, music beyond an ambient loop and drums, save/load, hand-drawn art.
