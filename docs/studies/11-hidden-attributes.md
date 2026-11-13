# Study 11: which hidden and personality attributes matter?

**Status:** done (12 November, 12,800 matches). Two views to test:
- FM Arena's position is that, of the hidden attributes, only Consistency affects a match.
- Another tester found that Pressure has the biggest effect on win rate, ahead of Consistency and Important Matches.
- A third question: does Important Matches only count in big matches?

**In short: not Consistency; Pressure, at the low end.**
- **Pressure is the only clear effect on results.** A squad with Pressure 1 loses 0.15 expected points per game
  (t −5.0 over league and European fixtures together), about 6 points a season, and picks up more cards.
- **Consistency barely matters.** In the two league fixtures used, the engine does not even read it in most
  matches.
- **Important Matches is not worth more on European nights** than in the league.
- **Dirtiness and Temperament change discipline, not results.** Dirtiness 20 adds a full card per game, and
  Temperament 1 half a card, without measurably changing results.
- **Other low values may hurt a little** (Professionalism and Sportsmanship at 1, Ambition at 1), but none passes
  |t| 3.

## Design

- **Neutral ground,** as in Studies 7, 9, 10 and 20:
  - The synthetic Premier League middle-eight squad on both sides, Gegenpress.
  - Tactical familiarity held at 80.
  - Four preset opponents, home and away.
- **League:** two league template matches between other clubs. The whole squad set to:
  - **1, 10 and 20:** Consistency, Important Matches, Injury Proneness, Dirtiness, Versatility, and the personality
    fields Pressure, Professionalism and Temperament;
  - **1 and 20:** Sportsmanship, Ambition, Loyalty and Adaptability.
- **European nights:** four real European ties between other clubs as templates.
  Important Matches, Consistency and Pressure at 1 and 20.
  - **Why fixtures:** the match input has no match-importance field that can be edited, so "big match" means "a real
    European night's template".
- **Not tested: Controversy.** It is not part of the match input.
- **Paired:** 40 seeds, giving 320 pairs per condition, each against the same match with the squad unchanged.
- **The squad's own values:** most fields sit around 12-14 (Pressure 8-16, median 13; Consistency 11-17). Injury
  Proneness (median 8) and Dirtiness (median 9) are lower.

## League fixtures

Per game against the same matches unchanged; t in brackets (|t| ≥ 4 established, 3-4 likely, below that unconfirmed).
Cards are the tested side's yellow and red cards.

| Attribute | Set to | xPts | xG difference | Shots | Shots against | Cards |
|---|---|---|---|---|---|---|
| **Pressure** | 1 | **−0.18 (−4.1)** | −0.29 (−3.9) | −1.3 | +0.9 | +0.37 (+3.8) |
| | 10 | +0.07 (+1.7) | +0.13 (+1.9) | +0.3 | −0.1 | +0.25 (+2.6) |
| | 20 | +0.08 (+2.0) | +0.15 (+2.2) | +0.7 | −0.4 | +0.00 |
| Sportsmanship | 1 | −0.12 (−2.9) | −0.19 (−2.7) | −1.6 | +0.4 | +0.14 |
| | 20 | +0.05 (+1.2) | +0.10 (+1.4) | +0.6 | −0.1 | −0.04 |
| Professionalism | 1 | −0.11 (−2.7) | −0.17 (−2.5) | −0.7 | +0.5 | +0.21 (+2.0) |
| | 10 | −0.00 (−0.0) | +0.02 (+0.4) | +0.2 | +0.4 | +0.12 |
| | 20 | +0.03 (+0.7) | +0.06 (+0.8) | +0.3 | +0.2 | +0.02 |
| Ambition | 1 | −0.08 (−1.9) | −0.12 (−1.7) | −0.4 | +0.3 | +0.20 (+2.0) |
| | 20 | +0.04 (+1.0) | +0.11 (+1.6) | +0.3 | −0.1 | −0.04 |
| Important Matches | 1 | −0.04 (−1.0) | −0.06 (−0.8) | −0.1 | +0.5 | +0.13 |
| | 10 | +0.02 (+0.6) | +0.05 (+0.7) | +0.1 | +0.2 | +0.16 |
| | 20 | +0.09 (+2.2) | +0.19 (+2.6) | +0.7 | −0.2 | +0.01 |
| Consistency | 1 | −0.00 (−0.2) | −0.01 (−0.3) | +0.0 | +0.2 | −0.04 |
| | 10 | +0.01 (+0.6) | +0.03 (+0.9) | +0.2 | −0.0 | +0.03 |
| | 20 | +0.04 (+2.0) | +0.06 (+1.9) | +0.2 | +0.0 | +0.00 |
| Dirtiness | 1 | +0.03 (+0.8) | +0.07 (+1.1) | +0.6 | −0.0 | **−0.57 (−6.3)** |
| | 10 | −0.01 (−0.4) | +0.00 (+0.0) | −0.2 | +0.1 | +0.18 (+2.2) |
| | 20 | +0.02 (+0.4) | +0.05 (+0.8) | +0.1 | −0.1 | **+1.00 (+9.7)** |
| Temperament | 1 | +0.03 (+0.7) | +0.07 (+1.0) | +0.2 | +0.1 | **+0.52 (+5.2)** |
| | 10 | +0.02 (+0.6) | +0.04 (+0.6) | +0.5 | +0.3 | +0.03 |
| | 20 | −0.01 (−0.1) | −0.00 (−0.0) | −0.0 | +0.3 | +0.00 |
| Versatility | 1 / 10 / 20 | +0.04 / +0.01 / +0.03 | all \|t\| ≤ 1.2 | | | |
| Injury Proneness | 1 / 10 / 20 | +0.00 / +0.00 / +0.01 | all \|t\| ≤ 0.3 | | | |
| Loyalty | 1 / 20 | +0.01 / −0.01 | all \|t\| ≤ 0.7 | | | |
| Adaptability | 1 / 20 | +0.04 / −0.03 | all \|t\| ≤ 1.1 | | | |

- **Pressure 1 is the one established effect:**
  - −1.3 shots per game and +0.9 shots against, so worse at both ends;
  - more cards.
  - The squad's own Pressure is 8-16, so raising it to 20 gains less (+0.07 xPts pooled, t 2.4, unconfirmed). The
    damage is at the bottom.
- **Low Sportsmanship and low Professionalism** cost about 0.11-0.12 xPts (t about −2.8). With 32 conditions, one or
  two values like these can appear by chance. They are worth a rerun, not a conclusion.
- **Dirtiness and Temperament drive cards:**
  - Dirtiness 20: a full extra card per game; Dirtiness 1: half a card fewer.
  - Temperament 1: half a card more.
  - Neither changes results measurably in 90 minutes. Suspensions over a season are not part of a single match.
- **Injury Proneness changes nothing measurable** within a match. Injuries over a season are outside this test.

## European nights

| Attribute | Set to | League: xPts | European nights: xPts | European minus league |
|---|---|---|---|---|
| Important Matches | 1 | −0.04 (−1.0) | −0.05 (−1.1) | −0.01 (t −0.1) |
| | 20 | +0.09 (+2.2) | +0.03 (+0.8) | −0.06 (t −1.1) |
| Consistency | 1 | −0.00 (−0.2) | −0.07 (−1.6) | −0.06 (t −1.4) |
| | 20 | +0.04 (+2.0) | +0.02 (+0.4) | −0.02 (t −0.5) |
| Pressure | 1 | −0.18 (−4.1) | −0.12 (−2.9) | +0.05 (t +0.9) |
| | 20 | +0.08 (+2.0) | +0.06 (+1.4) | −0.02 (t −0.4) |

- **No attribute is worth more on a European night.** Important Matches 20 is, if anything, worth less there (+0.03
  against +0.09, difference not significant).
- **Pooled over both kinds of fixture:**
  - Pressure 1: −0.15 xPts (t −5.0);
  - Important Matches 20: +0.06 (t 2.1);
  - Consistency 20: +0.03 (t 1.2).
- In the European fixtures the unchanged side gains more points (1.64 a game against 1.49). That comes from the
  stadiums and conditions of those templates, not from anything the tested side has.

## Where Consistency is read

Changing a field normally changes how every match unfolds, even when the average result stays the same. Consistency
does not behave that way.

In the league fixtures the same 240 of 320 matches replay exactly, at Consistency 1, 10 and 20:
- **Changed:** every match in one template (Leeds United v Tottenham Hotspur's ground and conditions) with the tested
  side as the away team.
- **Unchanged:** every match in that template with the tested side at home, and every match in the other template.

In the four European templates Consistency changes almost every match, home or away.

| | Consistency 1 | Consistency 10 | Consistency 20 |
|---|---|---|---|
| xPts where it is read (80 league pairs) | −0.02 (−0.2) | +0.05 (+0.6) | +0.16 (+2.0) |

- **The gate is a property of the fixture and side,** not of the players: the engine reads Consistency only when
  something in the template allows it, and acts the same way at every level.
- **What that something is remains open.** A per-side importance or "pressure of the occasion" value carried in
  the template would fit. That value would also be what Important Matches answers to.
- **Where it is read, Consistency points the expected way** (the higher the better), but with small samples.
- **Next step:** find the template field that gates it. If it exists and can be set, a proper big-match test becomes
  possible.

## So: is it "Consistency only"?

**No.**
- **Consistency** is the hidden attribute FM Arena singles out, but it has no measurable effect in these matches,
  and in ordinary league fixtures the engine often doesn't read it at all.
- **Pressure,** a personality field, is the one clear effect: a squad that crumbles under pressure (Pressure 1)
  loses about 6 points a season.
- **The tester who ranked Pressure first** is borne out. Their ranking of Consistency and Important Matches next is
  not: neither is clearly above zero.

## Caveats

- **Whole squad, one squad, one style.** Every player set to the same value; Premier League middle eight; Gegenpress.
- **One match at a time.** Effects that build over a season (injuries, suspensions, development, morale, dressing
  room) are not measured.
- **Big matches are approximated** with real European fixtures, because importance can't be set. If importance
  lives in a field that the gate above reveals, this part should be redone.
- **Controversy is not tested:** it isn't part of the match input.
- **Many conditions:** 38 conditions over two kinds of fixture, so expect one or two |t| of 2-3 by chance.

## Reproduce

```sh
.venv/bin/python port/validation/neutral_study.py build 11 runs/study11
.venv/bin/python port/validation/neutral_study.py pilot runs/study11 --workers 7
.venv/bin/python port/validation/neutral_study.py run runs/study11 --workers 7    # about 1.5 hours with 7 workers
.venv/bin/python port/validation/neutral_study.py report runs/study11
```

The templates are saved matches between other clubs (for example from `scripts/import_other_matches.py`), four of
them European ties; only their stadium, conditions and occasion are used.
