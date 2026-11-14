# CASSIUS — playable vertical slice (Godot 4.3+)

Open Godot 4.3 or newer → **Import** → pick `project.godot` → press **F5**.
The first open imports the PNG/WAV/font assets automatically.

> Run and checked in Godot 4.7: title, intro, march, camp, doctrine tree, muster, events, stall, altar, toll, crossroads, all four regions and the ending. The battle has not been play-tested yet.
> If text looks wrong, delete `assets/ui/pixel.fnt` and the game falls back to the engine font.

## The loop
March (side-scroll) → camp / dilemma / stall / altar → battle → crossroads → repeat ×5 → the Great Altar.

| Screen | Keys |
|---|---|
| Menus | arrows / `Tab` move, `Enter` chooses, `Esc` closes (mouse works too) |
| March | `WASD` ride (8-way), `Shift` gallop, `F` interact, `I` baggage, `L` ledger, `M` map, `Esc` close |
| Battle – deploy | drag banners inside the marked ground, `1`–`5` formation, right-drag to set facing, `Enter` begin |
| Battle – fight | left-click / drag-box select (Shift adds), right-click move, right-click an enemy to attack, right-drag to set facing, `1`–`5` formation, `R` retreat & rest, `H` halt, `V` volley (archers, then click), `Space` pause |

## What is in
- The march is a real 3D scene seen Hades-style: tilted orthographic camera, low-poly props (tents, stall, altar, forest) lit by a moving sun with shadows, rendered at 480×270 so it reads as pixel art; characters are pixel sprites standing in the 3D world. Kingdom palette, 2.35:1 letterbox, river, drifting fog, firelight. Walking the road moves the sun: dawn at camp, dusk at the battle marker, night at the crossroads.
- Four regional palettes (Empire, Thorncrown, Frostbay, Duskviolet) with their own enemies, altar preferences and dilemmas.
- Regiment battles: up to 7 regiments × 35 men, per-soldier health/attack timers, regiment-wide stats, the design doc's additive damage formula, all listed formations with a 3 s reform + 10 s cooldown, charges, rear attacks, volleys, retreat-and-heal, promotion by kills, rout, hidden flank forces.
- Roman denarius with the King's head, doctrine tree with coin burst, stall, baggage, ledger, omens, promises, non-judging settlement ending.

## Where things live
- `scripts/game.gd` — every number: units, formations, items, doctrines, regions, quota. Tune here.
- `scripts/expedition.gd` — the march and all menus/events. `scripts/battle.gd` — the battle. `scripts/ending.gd`, `scripts/intro.gd`.
- `shaders/` — water3d and fog are used by the march; sky and water are left over from the side-view version.
- `tools/gen_assets.py` — regenerates every sprite, background, icon, the font and all sounds (`python3 tools/gen_assets.py`, needs Pillow + numpy). All art is procedural placeholder in the target style; swap PNGs of the same size to replace it.

See `DESIGN_NOTES.md` for where this build deliberately departs from the design doc and why.

## For testing
- Debug builds only: `PageDown` (or `]`) jumps the column to the next stop on the road.
- Every run writes `logs/godot.log` in the project folder; script errors land there.
