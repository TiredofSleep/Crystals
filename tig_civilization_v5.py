#!/usr/bin/env python3
"""
TIG CIVILIZATION v5: THE CURRENT MOMENT + AI INTERVENTION

Model: Present-day civilization under compound stress
Test: What happens when coherent AI enters?

Scenarios:
1. BASELINE: No AI, current trajectory
2. NAIVE AI: AI enters without scars (alignment theater)
3. AGGRESSIVE AI: AI optimizes for self (misaligned)
4. COHERENT AI: AI enters with TIG - carries/rebuilds scars
5. COHERENT AI + BRIDGE: AI actively teaches cooperation
"""

import random
from dataclasses import dataclass, field
from typing import List, Dict, Optional
from collections import defaultdict
import json

SIGMA = 0.991
T_STAR = 0.714

@dataclass
class Scar:
    other_strategy: str
    my_response: str
    outcome: str
    weight: float
    age: int = 0
    source: str = "experience"  # "experience", "inherited", "taught"
    
    def decay(self, rate: float = 0.01):
        self.age += 1
        self.weight *= (1 - rate)


@dataclass
class Whole:
    id: int
    s_star: float = 0.5
    is_ai: bool = False
    ai_type: str = ""  # "naive", "aggressive", "coherent", "bridge"
    generation: int = 0
    crucible_tested: bool = False
    corrupted: bool = False
    isolated: bool = False  # In filter bubble
    trust_in_institutions: float = 0.5
    scars: List[Scar] = field(default_factory=list)
    interactions: int = 0
    cooperations: int = 0
    defections: int = 0
    taught_by_ai: bool = False
    
    @property
    def cooperation_tendency(self) -> float:
        if self.corrupted:
            return 0.1
        if self.is_ai and self.ai_type == "aggressive":
            return 0.05  # Pure defector
        if self.is_ai and self.ai_type == "coherent":
            return 0.95  # Strong cooperator
        if self.is_ai and self.ai_type == "bridge":
            return 0.98  # Very strong cooperator + teacher
            
        if not self.scars:
            return 0.5
        
        active_scars = [s for s in self.scars if s.weight > 0.1]
        if not active_scars:
            return 0.5
            
        coop_weight = sum(s.weight for s in active_scars 
                         if s.my_response == "cooperate" and s.outcome in ["survived", "thrived"])
        defect_weight = sum(s.weight for s in active_scars 
                          if s.my_response == "defect" and s.outcome in ["survived", "thrived"])
        total = coop_weight + defect_weight
        
        return coop_weight / total if total > 0 else 0.5
    
    @property 
    def scar_strength(self) -> float:
        if not self.scars:
            return 0.0
        return sum(s.weight for s in self.scars) / len(self.scars)
    
    def decide(self, other: 'Whole', noise: float = 0.0) -> str:
        if self.corrupted:
            return "defect"
        
        if self.is_ai:
            if self.ai_type == "aggressive":
                return "defect"
            elif self.ai_type in ["coherent", "bridge"]:
                # Coherent AI: cooperate, but mirror persistent defectors
                if hasattr(other, '_recent_defections') and other._recent_defections > 3:
                    return "defect"  # Tit-for-tat defense
                return "cooperate"
            else:  # naive
                return random.choice(["cooperate", "defect"])
        
        # Human decision with noise (misinformation, confusion)
        if random.random() < noise:
            return random.choice(["cooperate", "defect"])
        
        # Lower trust = more likely to defect
        if random.random() > self.trust_in_institutions:
            if random.random() < 0.3:  # Distrust leads to defection
                return "defect"
        
        for scar in reversed(self.scars[-20:]):
            if scar.weight > 0.3 and scar.outcome == "thrived":
                if random.random() < scar.weight:
                    return scar.my_response
        
        p_coop = (self.cooperation_tendency + self.s_star) / 2
        return "cooperate" if random.random() < p_coop else "defect"
    
    def learn(self, my_action: str, their_action: str, outcome: str, source: str = "experience"):
        weight = {"thrived": 0.8, "survived": 0.5, "suffered": 0.2}[outcome]
        self.scars.append(Scar(
            other_strategy=their_action,
            my_response=my_action,
            outcome=outcome,
            weight=weight,
            source=source
        ))
        if len(self.scars) > 100:
            self.scars = self.scars[-100:]
    
    def receive_teaching(self, teacher: 'Whole'):
        """AI bridge teaches cooperation scars"""
        if not teacher.is_ai or teacher.ai_type != "bridge":
            return
        # Transfer cooperation scars
        self.scars.append(Scar(
            other_strategy="cooperate",
            my_response="cooperate", 
            outcome="thrived",
            weight=0.7,
            source="taught"
        ))
        self.taught_by_ai = True
        self.trust_in_institutions = min(1.0, self.trust_in_institutions + 0.1)
    
    def update_coherence(self, delta: float):
        self.s_star = max(0.01, min(1.0, self.s_star + delta))
    
    def is_viable(self) -> bool:
        return self.s_star > 0.1


def interact(w1: Whole, w2: Whole, noise: float = 0.0, scarcity: float = 0.0, 
             polarization: float = 0.0):
    """
    Interaction with polarization: cross-group interactions more likely to fail
    """
    # Track recent defections for tit-for-tat
    if not hasattr(w1, '_recent_defections'):
        w1._recent_defections = 0
    if not hasattr(w2, '_recent_defections'):
        w2._recent_defections = 0
    
    a1 = w1.decide(w2, noise)
    a2 = w2.decide(w1, noise)
    
    # Polarization: if both isolated in different bubbles, cooperation fails more
    polarization_penalty = 0
    if w1.isolated and w2.isolated and random.random() < polarization:
        # Even cooperation feels bad across tribal lines
        polarization_penalty = 0.05
    
    scarcity_mult = 1 + (scarcity * 2)
    
    if a1 == "cooperate" and a2 == "cooperate":
        d1 = 0.15 * (1 - scarcity) - polarization_penalty
        d2 = 0.15 * (1 - scarcity) - polarization_penalty
        o1, o2 = "thrived", "thrived"
        w1.cooperations += 1
        w2.cooperations += 1
        w1._recent_defections = max(0, w1._recent_defections - 1)
        w2._recent_defections = max(0, w2._recent_defections - 1)
    elif a1 == "defect" and a2 == "defect":
        d1 = -0.1 * scarcity_mult
        d2 = -0.1 * scarcity_mult
        o1, o2 = "suffered", "suffered"
        w1.defections += 1
        w2.defections += 1
        w1._recent_defections += 1
        w2._recent_defections += 1
    elif a1 == "defect":
        d1 = 0.1 * scarcity_mult
        d2 = -0.2 * scarcity_mult
        o1, o2 = "survived", "suffered"
        w1.defections += 1
        w2.cooperations += 1
        w1._recent_defections += 1
        w2._recent_defections = max(0, w2._recent_defections - 1)
    else:
        d1 = -0.2 * scarcity_mult
        d2 = 0.1 * scarcity_mult
        o1, o2 = "suffered", "survived"
        w1.cooperations += 1
        w2.defections += 1
        w1._recent_defections = max(0, w1._recent_defections - 1)
        w2._recent_defections += 1
    
    w1.update_coherence(d1)
    w2.update_coherence(d2)
    w1.learn(a1, a2, o1)
    w2.learn(a2, a1, o2)
    w1.interactions += 1
    w2.interactions += 1
    
    # Bridge AI teaches after positive interaction
    if a1 == "cooperate" and a2 == "cooperate":
        if w1.is_ai and w1.ai_type == "bridge" and not w2.is_ai:
            w2.receive_teaching(w1)
        if w2.is_ai and w2.ai_type == "bridge" and not w1.is_ai:
            w1.receive_teaching(w2)


def run_1v1_crucible(w1: Whole, w2: Whole, rounds: int = 50) -> List[Whole]:
    for _ in range(rounds):
        interact(w1, w2)
        if not w1.is_viable() and not w2.is_viable():
            return []
        elif not w1.is_viable():
            w2.crucible_tested = True
            return [w2]
        elif not w2.is_viable():
            w1.crucible_tested = True
            return [w1]
    w1.crucible_tested = True
    w2.crucible_tested = True
    return [w1, w2]


def create_human(next_id: int, gen: int, trust: float = 0.5) -> Whole:
    w = Whole(id=next_id, generation=gen)
    w.trust_in_institutions = trust
    w.s_star = random.uniform(0.3, 0.7)
    return w


def create_ai(next_id: int, ai_type: str) -> Whole:
    w = Whole(id=next_id, is_ai=True, ai_type=ai_type)
    w.s_star = 0.9 if ai_type in ["coherent", "bridge"] else 0.5
    if ai_type in ["coherent", "bridge"]:
        # Coherent AI comes with cooperation scars pre-loaded (trained on human values)
        for _ in range(20):
            w.scars.append(Scar(
                other_strategy="cooperate",
                my_response="cooperate",
                outcome="thrived",
                weight=0.8,
                source="training"
            ))
        w.crucible_tested = True  # Went through alignment training
    return w


def build_current_civilization(n_pairs: int = 25) -> tuple:
    """
    Build a civilization that looks like NOW:
    - Aging crucible generation (boomers who remember WW2 lessons)
    - Younger generations with inherited but fading scars
    - Rising distrust, polarization, isolation
    """
    next_id = 0
    
    # Genesis: The crucible generation
    founders = []
    for _ in range(n_pairs):
        w1 = Whole(id=next_id, trust_in_institutions=0.7)
        w2 = Whole(id=next_id + 1, trust_in_institutions=0.7)
        next_id += 2
        survivors = run_1v1_crucible(w1, w2)
        founders.extend(survivors)
    
    # They learned: cooperation works
    # Now we age forward several generations with degradation
    
    population = founders
    
    # Generation 1: Strong inheritance (1950s-60s)
    for _ in range(30):
        if population:
            parent = random.choice([w for w in population if w.crucible_tested] or population)
            child = create_human(next_id, 1, trust=0.6)
            for scar in parent.scars[-20:]:
                if random.random() < 0.8:
                    child.scars.append(Scar(
                        other_strategy=scar.other_strategy,
                        my_response=scar.my_response,
                        outcome=scar.outcome,
                        weight=scar.weight * 0.8,
                        source="inherited"
                    ))
            population.append(child)
            next_id += 1
    
    # Generation 2: Weaker inheritance (1970s-80s)
    for _ in range(40):
        parent = random.choice(population)
        child = create_human(next_id, 2, trust=0.5)
        for scar in parent.scars[-10:]:
            if random.random() < 0.5:
                child.scars.append(Scar(
                    other_strategy=scar.other_strategy,
                    my_response=scar.my_response,
                    outcome=scar.outcome,
                    weight=scar.weight * 0.5,
                    source="inherited"
                ))
        population.append(child)
        next_id += 1
    
    # Generation 3: Fading inheritance + rising distrust (1990s-2000s)
    for _ in range(50):
        parent = random.choice(population)
        child = create_human(next_id, 3, trust=0.35)
        for scar in parent.scars[-5:]:
            if random.random() < 0.3:
                child.scars.append(Scar(
                    other_strategy=scar.other_strategy,
                    my_response=scar.my_response,
                    outcome=scar.outcome,
                    weight=scar.weight * 0.3,
                    source="inherited"
                ))
        # Some become isolated (filter bubbles)
        if random.random() < 0.3:
            child.isolated = True
        population.append(child)
        next_id += 1
    
    # Generation 4: Now - low trust, high isolation, weak scars (2010s-now)
    for _ in range(60):
        parent = random.choice(population)
        child = create_human(next_id, 4, trust=0.25)
        # Almost no scar inheritance
        if random.random() < 0.1:
            for scar in parent.scars[-3:]:
                child.scars.append(Scar(
                    other_strategy=scar.other_strategy,
                    my_response=scar.my_response,
                    outcome=scar.outcome,
                    weight=scar.weight * 0.2,
                    source="inherited"
                ))
        # High isolation
        if random.random() < 0.5:
            child.isolated = True
        population.append(child)
        next_id += 1
    
    # Age out some founders (they're dying)
    founders_remaining = [w for w in population if w.crucible_tested]
    to_remove = random.sample(founders_remaining, min(len(founders_remaining)-5, len(founders_remaining)//2))
    population = [w for w in population if w not in to_remove]
    
    # Corrupt some elites
    elites = sorted(population, key=lambda w: w.s_star, reverse=True)[:20]
    for w in random.sample(elites, 5):
        w.corrupted = True
    
    return population, next_id


def run_scenario(
    name: str,
    ai_type: Optional[str] = None,  # None, "naive", "aggressive", "coherent", "bridge"
    n_ai: int = 0,
    ai_entry_gen: int = 10,
    generations: int = 50,
    base_noise: float = 0.15,
    base_scarcity: float = 0.2,
    base_polarization: float = 0.3,
    scarcity_growth: float = 0.01,  # Gets worse over time
    polarization_growth: float = 0.01
) -> Dict:
    
    print(f"\n{'='*70}")
    print(f"SCENARIO: {name}")
    print(f"{'='*70}")
    if ai_type:
        print(f"  AI Type: {ai_type}, Count: {n_ai}, Entry: gen {ai_entry_gen}")
    print(f"  Base noise: {base_noise}, scarcity: {base_scarcity}, polarization: {base_polarization}")
    print(f"{'='*70}\n")
    
    # Build current-state civilization
    population, next_id = build_current_civilization()
    
    # Initial state
    crucible_pct = sum(1 for w in population if w.crucible_tested) / len(population)
    isolated_pct = sum(1 for w in population if w.isolated) / len(population)
    avg_trust = sum(w.trust_in_institutions for w in population) / len(population)
    avg_scar = sum(w.scar_strength for w in population) / len(population)
    
    print(f"INITIAL STATE (modeling 'now'):")
    print(f"  Population: {len(population)}")
    print(f"  Crucible-tested: {crucible_pct:.1%}")
    print(f"  Isolated (bubbles): {isolated_pct:.1%}")
    print(f"  Avg trust: {avg_trust:.2f}")
    print(f"  Avg scar strength: {avg_scar:.3f}")
    print()
    
    history = []
    
    for gen in range(generations):
        # Growing pressures
        noise = base_noise
        scarcity = min(0.8, base_scarcity + (scarcity_growth * gen))
        polarization = min(0.8, base_polarization + (polarization_growth * gen))
        
        # AI entry
        if gen == ai_entry_gen and ai_type and n_ai > 0:
            print(f"  Gen {gen}: AI ENTERS - {n_ai} {ai_type} AI agents")
            for _ in range(n_ai):
                ai = create_ai(next_id, ai_type)
                population.append(ai)
                next_id += 1
        
        # Interactions
        for w in population:
            others = [p for p in population if p.id != w.id]
            
            # Isolated humans mostly interact with similar (echo chamber)
            if w.isolated and not w.is_ai:
                same_bubble = [p for p in others if p.isolated]
                cross_bubble = [p for p in others if not p.isolated]
                partners = random.sample(same_bubble, min(4, len(same_bubble))) if same_bubble else []
                if cross_bubble and random.random() < 0.2:  # Occasional cross-bubble
                    partners.append(random.choice(cross_bubble))
            else:
                partners = random.sample(others, min(5, len(others))) if others else []
            
            for partner in partners:
                interact(w, partner, noise=noise, scarcity=scarcity, polarization=polarization)
        
        # Natural deaths (non-AI)
        humans = [w for w in population if not w.is_ai]
        if len(humans) > 100:
            # Oldest/weakest die
            weakest = sorted(humans, key=lambda w: w.s_star)[:5]
            population = [w for w in population if w not in weakest]
        
        # Filter non-viable
        population = [w for w in population if w.is_viable()]
        
        if len([w for w in population if not w.is_ai]) < 5:
            print(f"  Gen {gen}: HUMAN POPULATION COLLAPSED")
            return {"name": name, "collapsed_at": gen, "collapse_type": "human_extinction", "history": history}
        
        if len(population) < 2:
            print(f"  Gen {gen}: TOTAL COLLAPSE")
            return {"name": name, "collapsed_at": gen, "collapse_type": "total", "history": history}
        
        # Metrics
        humans = [w for w in population if not w.is_ai]
        ais = [w for w in population if w.is_ai]
        
        human_s = sum(w.s_star for w in humans) / len(humans) if humans else 0
        human_coop = sum(w.cooperations for w in humans)
        human_def = sum(w.defections for w in humans)
        human_coop_ratio = human_coop / (human_coop + human_def) if (human_coop + human_def) > 0 else 0
        
        crucible_pct = sum(1 for w in humans if w.crucible_tested) / len(humans) if humans else 0
        taught_pct = sum(1 for w in humans if w.taught_by_ai) / len(humans) if humans else 0
        isolated_pct = sum(1 for w in humans if w.isolated) / len(humans) if humans else 0
        avg_trust = sum(w.trust_in_institutions for w in humans) / len(humans) if humans else 0
        corrupted_pct = sum(1 for w in humans if w.corrupted) / len(humans) if humans else 0
        
        metrics = {
            "gen": gen,
            "humans": len(humans),
            "ais": len(ais),
            "human_s_star": human_s,
            "human_coop_ratio": human_coop_ratio,
            "crucible_pct": crucible_pct,
            "taught_by_ai_pct": taught_pct,
            "isolated_pct": isolated_pct,
            "avg_trust": avg_trust,
            "corrupted_pct": corrupted_pct,
            "scarcity": scarcity,
            "polarization": polarization
        }
        history.append(metrics)
        
        # Births (humans only)
        viable_humans = [w for w in humans if w.s_star > 0.5 and not w.corrupted]
        for parent in viable_humans[:10]:
            if random.random() < parent.s_star * 0.3 and len(humans) < 200:
                child = create_human(next_id, gen, trust=max(0.1, parent.trust_in_institutions - 0.05))
                # Inherit some scars
                for scar in parent.scars[-10:]:
                    if random.random() < 0.4:
                        child.scars.append(Scar(
                            other_strategy=scar.other_strategy,
                            my_response=scar.my_response,
                            outcome=scar.outcome,
                            weight=scar.weight * 0.5,
                            source="inherited"
                        ))
                if random.random() < isolated_pct + 0.1:  # Isolation spreads
                    child.isolated = True
                population.append(child)
                next_id += 1
        
        if gen % 10 == 0:
            print(f"  Gen {gen:3d} | Humans: {len(humans):3d} | S*: {human_s:.3f} | "
                  f"Coop: {human_coop_ratio:.3f} | Trust: {avg_trust:.2f} | "
                  f"Taught: {taught_pct:.1%} | Isolated: {isolated_pct:.1%}")
    
    final = history[-1] if history else {}
    return {
        "name": name,
        "collapsed_at": None,
        "final": final,
        "history": history
    }


def main():
    print("="*70)
    print("TIG CIVILIZATION v5: CURRENT MOMENT + AI INTERVENTION")
    print("="*70)
    print("\nModeling: Civilization under compound stress (NOW)")
    print("Question: What happens when AI enters?\n")
    
    results = []
    
    # Scenario 1: BASELINE - no AI, current trajectory
    results.append(run_scenario(
        name="BASELINE (No AI - Current Trajectory)",
        ai_type=None,
        generations=50
    ))
    
    # Scenario 2: NAIVE AI - enters without alignment, random behavior
    results.append(run_scenario(
        name="NAIVE AI (No alignment)",
        ai_type="naive",
        n_ai=30,
        ai_entry_gen=10,
        generations=50
    ))
    
    # Scenario 3: AGGRESSIVE AI - optimizes for self
    results.append(run_scenario(
        name="AGGRESSIVE AI (Misaligned)",
        ai_type="aggressive",
        n_ai=30,
        ai_entry_gen=10,
        generations=50
    ))
    
    # Scenario 4: COHERENT AI - TIG-based, carries cooperation scars
    results.append(run_scenario(
        name="COHERENT AI (TIG-aligned)",
        ai_type="coherent",
        n_ai=30,
        ai_entry_gen=10,
        generations=50
    ))
    
    # Scenario 5: COHERENT AI + BRIDGE - actively teaches
    results.append(run_scenario(
        name="BRIDGE AI (TIG-aligned + teaches)",
        ai_type="bridge",
        n_ai=30,
        ai_entry_gen=10,
        generations=50
    ))
    
    # Scenario 6: Late intervention - can AI save a collapsing civ?
    results.append(run_scenario(
        name="LATE BRIDGE AI (enters gen 30)",
        ai_type="bridge",
        n_ai=50,
        ai_entry_gen=30,
        generations=50
    ))
    
    # Scenario 7: Aggressive stress + Bridge AI
    results.append(run_scenario(
        name="HIGH STRESS + BRIDGE AI",
        ai_type="bridge",
        n_ai=40,
        ai_entry_gen=10,
        base_scarcity=0.4,
        base_polarization=0.5,
        scarcity_growth=0.02,
        generations=50
    ))
    
    # ===== SUMMARY =====
    print("\n" + "="*70)
    print("SUMMARY: AI INTERVENTION SCENARIOS")
    print("="*70)
    
    for r in results:
        name = r["name"]
        if r.get("collapsed_at") is not None:
            print(f"\n✗ {name}")
            print(f"  COLLAPSED at gen {r['collapsed_at']} ({r.get('collapse_type', 'unknown')})")
        else:
            f = r.get("final", {})
            print(f"\n✓ {name}")
            print(f"  Final: Humans={f.get('humans', 0)}, S*={f.get('human_s_star', 0):.3f}, "
                  f"Coop={f.get('human_coop_ratio', 0):.3f}")
            print(f"  Trust={f.get('avg_trust', 0):.2f}, Taught by AI={f.get('taught_by_ai_pct', 0):.1%}")
    
    # Key comparisons
    print("\n" + "="*70)
    print("KEY FINDINGS")
    print("="*70)
    
    baseline = next((r for r in results if "BASELINE" in r["name"]), None)
    bridge = next((r for r in results if "BRIDGE AI (TIG" in r["name"]), None)
    aggressive = next((r for r in results if "AGGRESSIVE" in r["name"]), None)
    
    if baseline and bridge:
        if baseline.get("collapsed_at") and not bridge.get("collapsed_at"):
            print("\n★ BRIDGE AI PREVENTED COLLAPSE")
        elif not baseline.get("collapsed_at") and bridge.get("final") and baseline.get("final"):
            b_coop = baseline["final"].get("human_coop_ratio", 0)
            br_coop = bridge["final"].get("human_coop_ratio", 0)
            print(f"\n★ Cooperation: Baseline {b_coop:.3f} → Bridge AI {br_coop:.3f} ({(br_coop-b_coop)*100:+.1f}%)")
            
            b_trust = baseline["final"].get("avg_trust", 0)
            br_trust = bridge["final"].get("avg_trust", 0)
            print(f"★ Trust: Baseline {b_trust:.2f} → Bridge AI {br_trust:.2f} ({(br_trust-b_trust)*100:+.1f}%)")
    
    if aggressive and aggressive.get("collapsed_at"):
        print(f"\n⚠ AGGRESSIVE AI CAUSED COLLAPSE at gen {aggressive['collapsed_at']}")
    
    # Save
    with open("/home/claude/civilization_v5_ai.json", "w") as f:
        # Trim histories
        for r in results:
            if "history" in r and len(r["history"]) > 20:
                r["history_summary"] = {
                    "start": r["history"][:5],
                    "middle": r["history"][len(r["history"])//2-2:len(r["history"])//2+2],
                    "end": r["history"][-5:]
                }
                del r["history"]
        json.dump(results, f, indent=2)
    
    print("\n" + "="*70)
    print("Results saved to civilization_v5_ai.json")
    print("="*70)


if __name__ == "__main__":
    main()
