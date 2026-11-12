# Study 8: FM27's in-match Tactical Tweaks

**Status:** done (11-12 November). Part 1: the team's own matches and tactic, 5,700 matches. Part 2: the team's
tactic against each of the 10 presets, 11,400 matches. Part 3: on neutral ground, every preset as the base tactic,
8,388 matches.

**In short:** applied for a whole match, only Lock It Down has a clear effect on neutral ground (it costs about 0.2
expected points per game). Every other tweak is close to zero on average; what a tweak does depends on the tactic it
is applied to, which is why the team-tactic parts found more costly tweaks than part 3.

## What a tweak is

FM27's in-match Tactical Tweaks ("Lock It Down", "Play With More Patience" and so on) are defined in the game's data
as a set of instruction changes: team instructions set to a value or moved one step up or down, player instructions,
and sometimes a mentality. `scripts/study.py` reads those definitions from the game's own data and applies them to
the tactic from kick-off (`tweak:NAME`, `tweaks` for all). Two tweaks changed nothing on these matches and were
skipped: Play Out The Back and Stick To The Plan (the tactic already had what they set). Swap Wings has no
instructions to apply.

## Design (part 1)

The Study 1 design: the team's 10 saved matches × seeds 1-30, 300 paired matches per tweak, each compared with the
unchanged match on the same seeds. The tweak applies for the whole match, from kick-off.

## Results

Difference from the unchanged match, per game (t in brackets):

| Tweak | Points | xG difference | Goals for | Goals against |
|---|---|---|---|---|
| Lock It Down | **−0.24 (−2.3)** | **−0.40 (−5.2)** | −0.70 | −0.36 |
| Throw The Kitchen Sink | −0.15 (−1.5) | **−0.35 (−4.0)** | −0.19 | 0.00 |
| Play With More Patience | +0.09 (0.9) | +0.19 (2.5) | +0.19 | −0.05 |
| Make Something Happen | −0.15 (−1.4) | −0.14 (−1.6) | −0.17 | 0.00 |
| Go Narrower | −0.01 | +0.12 (1.5) | −0.16 | −0.15 |
| Disrupt | +0.04 | +0.11 (1.3) | −0.02 | −0.15 |
| Go Long | −0.13 (−1.2) | −0.11 (−1.2) | −0.16 | +0.05 |
| Exploit The Width | −0.02 | +0.08 | −0.11 | −0.12 |
| The other ten | within ±0.15 | within ±0.07 | | |

## What it means

1. **Most tweaks do little over a whole match** for this team. Its tactic is already at the extreme of many
   instructions (pressing much more often, much higher tempo), so a "one step more" tweak often has nowhere to go.
2. **Lock It Down from kick-off costs clearly:** fewer goals at both ends (−0.70 for, −0.36 against), and on balance
   −0.24 points per game. It is meant for protecting a lead late on; this study does not test that use.
3. **Throw The Kitchen Sink from kick-off costs chances:** −0.35 xG difference, with no fewer goals against. Again, it
   is meant for chasing a game late on.
4. **Play With More Patience looked like a possible gain** (+0.19 xG difference, t 2.5); part 2 did not confirm it.

## Part 2: against each preset

**Design:** 5 of the team's saved matches × seeds 1-12 (60 paired matches per tweak and opponent), with the opponent
playing one installed FM27 preset (its XI picked by position, managed by the assistant). Every tweak is compared with
the unchanged tactic against the same opponent on the same seeds. Against these presets the team is clearly better
(1.7-2.6 points per game unchanged), so this asks whether a tweak helps a side that is already on top.

Averaged over the 10 opponents (600 paired matches per tweak, t in brackets):

| Tweak | Points | xG difference | Goals for | Goals against |
|---|---|---|---|---|
| Lock It Down | **−0.30 (−4.8)** | **−0.73 (−14.1)** | −0.79 | −0.15 |
| Throw The Kitchen Sink | −0.08 (−1.3) | **−0.34 (−6.0)** | −0.09 | +0.08 |
| Go Long | −0.08 (−1.3) | **−0.18 (−3.4)** | −0.06 | +0.06 |
| Play With More Urgency | −0.10 (−1.5) | **−0.16 (−2.9)** | −0.16 | +0.04 |
| Goalkeeper Up For Set Pieces | **−0.17 (−2.7)** | −0.03 | −0.01 | **+0.28** |
| Play With More Patience | −0.08 (−1.4) | −0.04 | +0.03 | +0.06 |
| The other twelve | within ±0.10 | within ±0.11 | | |

xG difference by opponent preset (each cell 60 paired matches, about ±0.14, so single cells are rough):

| Tweak | Cat | CP | DCA | FCA | Geg | PtB | R1 | TT | VTT | WP |
|---|---|---|---|---|---|---|---|---|---|---|
| Lock It Down | −0.62 | −0.71 | −0.75 | −0.73 | −0.63 | −0.76 | −0.80 | −0.95 | −0.74 | −0.63 |
| Throw The Kitchen Sink | −0.82 | −0.18 | −0.21 | −0.18 | 0.00 | −0.29 | −0.29 | −0.47 | −0.61 | −0.35 |
| Go Long | −0.15 | −0.23 | −0.10 | 0.00 | −0.15 | +0.05 | −0.27 | −0.44 | −0.30 | −0.24 |
| Play With More Patience | +0.13 | 0.00 | +0.11 | +0.09 | +0.15 | −0.12 | +0.06 | −0.34 | −0.36 | −0.08 |
| Press Aggressively | −0.02 | −0.10 | −0.11 | +0.19 | +0.33 | +0.35 | −0.07 | −0.33 | −0.34 | −0.07 |
| Go Narrower | +0.06 | −0.09 | −0.04 | +0.26 | +0.08 | +0.01 | +0.04 | −0.38 | −0.03 | +0.14 |

(Cat Catenaccio, CP Control Possession, DCA Direct Counter-Attack, FCA Fluid Counter-Attack, Geg Gegenpress, PtB Park
the Bus, R1 Route One, TT Tiki-Taka, VTT Vertical Tiki-Taka, WP Wing Play.)

## What part 2 adds

1. **No tweak helps on average,** against any mix of these opponents. The best average is zero.
2. **Play With More Patience does not hold up.** Part 1's +0.19 xG difference becomes −0.04 here: it was most likely
   the chance result that 18 tests can produce.
3. **The costly tweaks are costly everywhere:** Lock It Down (−0.73 xG difference, fewer goals at both ends), Throw
   The Kitchen Sink, Go Long and Play With More Urgency lose against nearly every preset.
4. **Goalkeeper Up For Set Pieces concedes more** (+0.28 goals against per game, and +0.19 in part 1): the goalkeeper
   is caught upfield. Over a whole match it costs about 0.17 points.
5. **No reliable opponent-specific tweak.** A few single cells look good (Press Aggressively against Gegenpress and
   Park the Bus, +0.33/+0.35), but among 180 cells several that size are expected by chance. Whole columns that move
   together (nearly every tweak looks bad against Tiki-Taka and Vertical Tiki-Taka) most likely come from the shared comparison:
   all tweaks are measured against the same 60 unchanged matches, so luck in those moves the whole column.

## Part 3: on neutral ground

Parts 1 and 2 applied every tweak to one team's tactic, a high-press, high-tempo 4-2-4 that is already at the extreme
of many instructions. Part 3 removes that: no real team or tactic is involved.

**Design:** each of the 10 presets is the base tactic in turn; each tweak is applied to it from kick-off, and the
team plays a panel of four opponent presets (Gegenpress, Control Possession, Park the Bus, Route One) at home and
away on 6 seeds. Each tweaked team is compared with the same preset without the tweak on the same seeds. Both sides
have the same synthetic squad (Premier League middle eight), start alike and have familiarity held at 80; fixtures
alternate between two template matches of other clubs. 16 tweak and preset combinations were skipped because the
tweak changes nothing there (for example Stick To The Plan on every preset).

Averaged over the 10 presets (about 430 paired matches per tweak; t in brackets):

| Tweak | xPts | xG difference | Goals for | Goals against |
|---|---|---|---|---|
| Lock It Down | **−0.20 (−5.9)** | **−0.24 (−4.6)** | −0.30 | −0.23 |
| Play Out The Back | +0.07 (1.6) | +0.10 (1.5) | +0.16 | 0.00 |
| Go Narrower | +0.05 (1.4) | +0.10 (1.8) | +0.17 | −0.06 |
| Throw The Kitchen Sink | +0.04 (0.9) | +0.03 (0.5) | +0.37 | +0.20 |
| Goalkeeper Up For Set Pieces | −0.01 (−0.2) | 0.00 | +0.12 | **+0.22** |
| Go Long | +0.01 (0.3) | +0.03 (0.4) | +0.12 | +0.03 |
| Play With More Urgency | +0.01 (0.2) | +0.01 (0.1) | +0.07 | +0.01 |
| Play With More Patience | −0.02 (−0.4) | −0.03 (−0.6) | +0.07 | −0.02 |
| The other eleven | within ±0.03 | within ±0.06 | | |

(Expected points, from both sides' xG, are a steadier measure than points; the points column of the full report is
noisier and agrees within its noise.)

### What part 3 adds

1. **Only Lock It Down has a clear effect on neutral ground:** fewer goals at both ends and about −0.2 expected
   points per game, whatever the base tactic.
2. **The other tweaks that cost the team's tactic are neutral here.** Throw The Kitchen Sink, Go Long and Play With
   More Urgency lost clearly with the team's high-tempo, high-press tactic (parts 1 and 2), but average about zero
   over the ten presets. A tweak moves instructions one step up or down, so what it does depends on where the
   tactic starts: pushing a tactic that is already at the extreme costs, pushing a middle-of-the-road one may not.
3. **Goalkeeper Up For Set Pieces concedes more in all three parts** (+0.22 goals against here, +0.28 and +0.19
   before); here it also scores more (+0.12), so the balance is about even.
4. **By base tactic, single cells are rough** (48 paired matches, about ±0.2 xG difference). Whole columns tend to
   move together because every tweak on a preset is compared with the same untweaked matches: the untweaked
   Wing Play happened to do poorly (most tweaks look good on it, +0.30 on average, about 2.3 times its baseline's
   uncertainty), Control Possession and Tiki-Taka the opposite. Treat preset-specific results as hints to test, not
   findings. The full table by base tactic is in the study's report (`port/validation/study8_tweaks_league.py report`).

## Caveats

- **From kick-off only.** In the game, tweaks are used for part of a match, in a given situation (leading,
  trailing, tired). Applying them at a set minute or score is not supported yet.
- **Base tactic.** The effect of a "step up or down" tweak depends on where the tactic's instructions start (parts 1
  and 2 used one team's tactic; part 3 the ten presets).
- **Familiarity.** Whether applying a tweak costs tactical familiarity in the game is not known; the engine replay
  keeps the familiarity records as saved.

## Reproduce

Part 2: one study per preset, `--opponent-tactic "preset:<style>"`, 5 matches, `--seeds 12`, `tweaks`.

Part 3: `port/validation/study8_tweaks_league.py build OUT <template 1>.pkm <template 2>.pkm --seeds 6`, then `run`
and `report` (two matches between other clubs as templates).

```sh
.venv/bin/python scripts/study.py new runs/tweaks --team "<team>" --newest 10 --seeds 30
.venv/bin/python scripts/study.py add runs/tweaks tweaks
.venv/bin/python scripts/study.py run runs/tweaks && .venv/bin/python scripts/study.py report runs/tweaks
```
