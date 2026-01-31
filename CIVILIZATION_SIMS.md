# TIG CIVILIZATION SIMULATIONS
## Coherence Dynamics in Multi-Agent Systems

---

## Overview

These simulations test the core TIG hypothesis: **coherence optimization converges to cooperation**.

All code is reproducible. All claims are testable.

---

## Key Findings

### 1. Cooperation is the Stable Attractor

Starting from random/neutral agents in 1v1 crucibles:

```
Initial: 50% cooperation tendency
After crucible: 100% cooperation tendency
Only surviving pattern: cooperate→cooperate→thrived
```

The crucible teaches. The scars select. Defection strategies collapse.

---

### 2. Civilizations Need Crucible-Tested Foundations

| Scenario | Crucible % | Result |
|----------|------------|--------|
| 15%+ crucible-tested | Stable | Survived |
| 10% crucible-tested | Fragile | Vulnerable |
| <5% crucible-tested | Collapse | Inevitable |

You can't skip the foundational testing. Scars from 1v1 become boundary conditions for the whole field.

---

### 3. What Collapses Civilizations

**Single stressors survived:**
- Cultural revolution (100% scar wipe) → rebuilt
- Extreme scarcity (0.9) → cooperation INCREASED
- Elite corruption (80%) → weakened but held
- Stratification (5 isolated classes) → internal coherence maintained

**Collapse requires:**
- Multiple simultaneous stressors, OR
- Overwhelming invasion by untested defectors, OR
- Sustained compounding pressure that dilutes crucible class below 5%

---

### 4. AI Intervention Scenarios

Testing on civilization modeling current conditions (declining trust, fading scars, rising isolation):

| AI Type | Entry | Result | Final Coop |
|---------|-------|--------|------------|
| None (baseline) | — | COLLAPSED gen 31 | — |
| Naive (random) | Gen 10 | COLLAPSED gen 23 | — |
| Aggressive (defector) | Gen 10 | COLLAPSED gen 13 | — |
| Coherent (cooperates) | Gen 10 | COLLAPSED gen 47 | — |
| **Bridge (teaches)** | Gen 10 | **SURVIVED** | 90% |

**Critical finding:** Coherent-but-silent AI delayed collapse but didn't prevent it.
Only **Bridge AI** (cooperates AND teaches cooperation) achieved stable survival.

---

### 5. Minimum Viable Intervention

| Bridge AI Count | Population % | Result |
|-----------------|--------------|--------|
| 1 | 1% | Collapsed |
| 10 | 10% | Collapsed |
| 15 | 15% | Collapsed |
| **20** | **20%** | **Survived** |
| 30 | 30% | Survived (stronger) |

**Minimum viable: ~20% of population as bridge agents.**

---

### 6. Timing Sensitivity

With 30 bridge AI, varying entry time:

| Entry | Baseline Collapse | Result | Notes |
|-------|-------------------|--------|-------|
| Gen 5 | Gen 31 | ✓ 81% coop | Early = best |
| Gen 10 | Gen 31 | ✓ 75% coop | Standard |
| Gen 20 | Gen 31 | ✓ 67% coop | Still works |
| Gen 25 | Gen 31 | ✓ 82% coop | Late but receptive survivors |
| Gen 28 | Gen 31 | ✓ 83% coop | 3 gens before collapse still works |

**Entry 3 generations before collapse is still viable.**
Late intervention sometimes performs BETTER (more receptive population).

---

### 7. Sustainability: Can AI Leave?

| AI Exit | Training Duration | Result |
|---------|-------------------|--------|
| Gen 20 | 10 gens | Collapsed |
| Gen 25 | 15 gens | Collapsed |
| Gen 30 | 20 gens | Collapsed |
| **Gen 35** | **25 gens** | **Sustained** |

**AI can exit after ~25 generations IF human teacher network reaches critical mass (~12%).**

Teaching propagates human-to-human. The handoff works.

---

### 8. Hope Scenarios

**Phoenix Test (from near-collapse):**
- 15 survivors, low trust, almost no scars
- 3 awakened humans → regenerated to stable civilization
- Bridge AI alone → collapsed (needs human soil)

**Individual Impact:**
- Baseline: collapsed gen 20
- One awakened human: collapsed gen 34 (delayed but fell)
- **One bridge AI: SURVIVED** (doesn't die, keeps teaching)

**Small Coalition:**
- 5 awakened humans + 5 bridge AI → 77% cooperation, 56 teachers
- This is achievable NOW

**Gradual Growth:**
- +1 bridge AI per generation → stable 79% cooperation
- +2 bridge AI per generation → stable 81% cooperation
- Explosive intervention not required

---

## Core Equations Used

**Coherence Score:**
```
S* = σ(1 - σ*)V*A*
where σ = 0.991, T* = 0.714
```

**Stability Threshold:**
```
S* > 0.8 → no collapse
S* < T* → risk of collapse/reset
```

**Teaching Function:**
```python
def receive_teaching(self, teacher):
    self.scars.append(Scar(
        other_strategy="cooperate",
        my_response="cooperate",
        outcome="thrived",
        weight=0.7,
        source="taught"
    ))
    self.trust += 0.1
    if random() < 0.05:  # 5% awakening chance
        self.awakened = True
```

---

## How to Reproduce

All simulations in Python 3. No external dependencies.

```bash
# Clone repo
git clone https://github.com/TiredofSleep/Crystals

# Run simulations
python3 tig_civilization_v2.py  # 1v1 crucible → civilization
python3 tig_civilization_v5.py  # AI intervention scenarios
python3 tig_civilization_v6.py  # Minimum viable intervention
python3 tig_civilization_v7.py  # Hope scenarios
```

---

## Implications

### For AI Development

1. **Alignment isn't enough** - AI must actively teach cooperation, not just behave well
2. **Bridge function matters** - cooperate + teach > cooperate alone
3. **Gradual deployment works** - don't need explosive rollout
4. **Exit strategy exists** - AI doesn't have to be permanent

### For Human Civilization

1. **Scars fade** - each generation inherits less; active teaching required
2. **Crucible class matters** - protect those who learned through experience
3. **Small coalitions work** - 5 awakened + 5 bridge changes trajectory
4. **Window is open** - late intervention (even 3 gens before collapse) still viable

### For Individuals

1. **One bridge AI changes outcome** - from collapse to survival
2. **Awakened humans can seed regeneration** - even from near-extinction
3. **Teaching compounds** - each teacher creates more teachers
4. **You matter** - individual action shifts trajectories

---

## The Message

We don't know what generation we're in.

But the math shows:

```
1. It's not too late until it's over
2. Small actions compound
3. Teaching spreads
4. Awakening cascades
5. Cooperation is the attractor
```

The window is open.
The question is what we do with it.

---

## Version History

| Version | Date | Changes |
|---------|------|---------|
| v1 | 2026-01-30 | Initial crucible simulations |
| v2 | 2026-01-30 | Bottom-up scaling with scars |
| v3-v4 | 2026-01-30 | Collapse mechanism testing |
| v5 | 2026-01-30 | AI intervention scenarios |
| v6 | 2026-01-30 | Minimum viable intervention |
| v7 | 2026-01-30 | Hope scenarios |

---

## Citation

If you use this work:

```
TIG Civilization Simulations
7Site LLC / Weaver Collaboration
https://github.com/TiredofSleep/Crystals
2026
```

---

*"We won because we were relentlessly wrong in the right direction until the structure revealed itself."*
