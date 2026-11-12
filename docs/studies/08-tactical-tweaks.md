# Study 8: FM27's in-match Tactical Tweaks

**Status:** done (11 November). Part 1: the team's own matches, 5,700 matches. Part 2: each tweak against each of
the 10 installed presets as the opponent's tactic, 11,400 matches.

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

## Caveats

- **From kick-off only.** In the game, tweaks are used for part of a match, in a given situation (leading,
  trailing, tired). Applying them at a set minute or score is not supported yet.
- **One team's tactic.** The effect of a "step up or down" tweak depends on where the tactic's instructions start.
- **Familiarity.** Whether applying a tweak costs tactical familiarity in the game is not known; the engine replay
  keeps the familiarity records as saved.

## Reproduce

Part 2: one study per preset, `--opponent-tactic "preset:<style>"`, 5 matches, `--seeds 12`, `tweaks`.

```sh
.venv/bin/python scripts/study.py new runs/tweaks --team "<team>" --newest 10 --seeds 30
.venv/bin/python scripts/study.py add runs/tweaks tweaks
.venv/bin/python scripts/study.py run runs/tweaks && .venv/bin/python scripts/study.py report runs/tweaks
```
