# Brand Brief — How it should look and feel

> Bound by [`AGENTS.md`](../../AGENTS.md). This guides every surface — dashboards,
> CLIs, reports, logs, docs — so UI/UX never drifts into hype or risk.

## 1. Essence

**Calm authority under load.** This is critical financial infrastructure. It should
feel like a cockpit or a risk desk: precise, sober, legible, and *trustworthy
precisely because it is restrained*. The promise is **"nothing happens that wasn't
proposed, decided, approved and recorded."**

## 2. Personality

| We are | We are not |
|--------|------------|
| Institutional, sober, precise | Flashy, gamified, hype-driven |
| Auditable, transparent, honest | Black-box, "trust me", magical |
| Calm, deliberate, fail-closed | Urgent, FOMO-inducing, aggressive |
| Evidence-led | Vibes-led |

## 3. Voice & tone

- **Plain, exact, quantified.** State facts and uncertainty plainly; surface
  confidence, drift and failure rather than hiding them.
- **No persuasion toward risk.** Never nudge a user toward trading; default copy
  steers to the safer option.
- Probabilities, not promises. Disagreement and unresolved questions are shown, not
  smoothed over.

## 4. Visual language (for dashboards/reports)

- **Information density over decoration:** tables, small multiples, clear units.
- **Status semantics are fixed and unambiguous:**
  - **Green** = healthy / approved / reconciled.
  - **Amber** = degraded / requires manual approval / paper-only / unknown.
  - **Red** = blocked / rejected / kill-switch active / fail-closed.
  - Red is never celebratory; green never implies "go bigger".
- **Mode is always visible** (research / paper / live-gated), with anything that
  could touch real capital given an unmistakable, deliberate treatment.
- **Provenance on demand:** any number can reveal its `trace_id` and identity chain.
- **Typography:** monospace for ids/prices/quantities; humanist sans for prose.

## 5. Anti-patterns (forbidden)

- Rockets, confetti, "to the moon", profit-porn, leaderboards, streaks.
- One-click "go live" or any frictionless path to real capital.
- Hiding errors, drift, or losses to look healthier.
- Dark patterns that increase risk-taking or obscure the kill switch.
- Presenting agent/tool output as authoritative or trusted by default.

## 6. The one-line brand test

> If a screen, report, or message would make a regulator nod and a gambler bored,
> it is on-brand.
