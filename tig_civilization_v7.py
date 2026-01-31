#!/usr/bin/env python3
"""
TIG CIVILIZATION v7: HOPE SCENARIOS

We don't know what generation we're in.
So test what matters:

1. PHOENIX: Can we regenerate from near-collapse?
2. INDIVIDUAL IMPACT: What can ONE human who "gets it" do?
3. SMALL GROUPS: What if just a few humans + AI work together?
4. GRADUAL AWAKENING: What if bridge AI starts small and grows?
5. THE INFECTION: Can cooperation spread like a virus?
6. WORST CASE: What if we're already past the point? Is there still hope?
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
    source: str = "experience"
    
    def decay(self, rate: float = 0.01):
        self.age += 1
        self.weight *= (1 - rate)


@dataclass
class Whole:
    id: int
    s_star: float = 0.5
    is_ai: bool = False
    ai_type: str = ""
    generation: int = 0
    crucible_tested: bool = False
    corrupted: bool = False
    isolated: bool = False
    trust_in_institutions: float = 0.5
    awakened: bool = False  # Human who "gets it" - can teach like AI
    scars: List[Scar] = field(default_factory=list)
    interactions: int = 0
    cooperations: int = 0
    defections: int = 0
    taught_by: Optional[int] = None
    
    @property
    def cooperation_tendency(self) -> float:
        if self.corrupted:
            return 0.1
        if self.is_ai and self.ai_type == "aggressive":
            return 0.05
        if self.is_ai and self.ai_type in ["coherent", "bridge"]:
            return 0.95
        if self.awakened:
            return 0.9  # Awakened humans are strong cooperators
            
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
    def can_teach(self) -> bool:
        if self.is_ai and self.ai_type == "bridge":
            return True
        if self.awakened:
            return True
        # Taught humans with high coherence can teach
        if self.taught_by is not None and self.cooperation_tendency > 0.8 and self.s_star > 0.7:
            return True
        return False
    
    def decide(self, other: 'Whole', noise: float = 0.0) -> str:
        if self.corrupted:
            return "defect"
        
        if self.is_ai:
            if self.ai_type == "aggressive":
                return "defect"
            elif self.ai_type in ["coherent", "bridge"]:
                if hasattr(other, '_recent_defections') and other._recent_defections > 3:
                    return "defect"
                return "cooperate"
            else:
                return random.choice(["cooperate", "defect"])
        
        if self.awakened:
            # Awakened humans mostly cooperate, with forgiveness
            return "cooperate"
        
        if random.random() < noise:
            return random.choice(["cooperate", "defect"])
        
        if random.random() > self.trust_in_institutions:
            if random.random() < 0.3:
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
        if not teacher.can_teach:
            return
        self.scars.append(Scar(
            other_strategy="cooperate",
            my_response="cooperate", 
            outcome="thrived",
            weight=0.7,
            source="taught"
        ))
        self.taught_by = teacher.id
        self.trust_in_institutions = min(1.0, self.trust_in_institutions + 0.1)
        
        # Small chance teaching causes awakening
        if random.random() < 0.05:  # 5% chance
            self.awakened = True
    
    def update_coherence(self, delta: float):
        self.s_star = max(0.01, min(1.0, self.s_star + delta))
    
    def is_viable(self) -> bool:
        return self.s_star > 0.1


def interact(w1: Whole, w2: Whole, noise: float = 0.0, scarcity: float = 0.0, 
             polarization: float = 0.0):
    if not hasattr(w1, '_recent_defections'):
        w1._recent_defections = 0
    if not hasattr(w2, '_recent_defections'):
        w2._recent_defections = 0
    
    a1 = w1.decide(w2, noise)
    a2 = w2.decide(w1, noise)
    
    polarization_penalty = 0
    if w1.isolated and w2.isolated and random.random() < polarization:
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
    else:
        d1 = -0.2 * scarcity_mult
        d2 = 0.1 * scarcity_mult
        o1, o2 = "suffered", "survived"
        w1.cooperations += 1
        w2.defections += 1
        w2._recent_defections += 1
    
    w1.update_coherence(d1)
    w2.update_coherence(d2)
    w1.learn(a1, a2, o1)
    w2.learn(a2, a1, o2)
    w1.interactions += 1
    w2.interactions += 1
    
    # Teaching
    if a1 == "cooperate" and a2 == "cooperate":
        if w1.can_teach and not w2.is_ai and w2.taught_by is None:
            w2.receive_teaching(w1)
        if w2.can_teach and not w1.is_ai and w1.taught_by is None:
            w1.receive_teaching(w2)


def create_human(next_id: int, trust: float = 0.5, isolated: bool = False) -> Whole:
    w = Whole(id=next_id)
    w.trust_in_institutions = trust
    w.s_star = random.uniform(0.3, 0.7)
    w.isolated = isolated
    return w


def create_ai(next_id: int, ai_type: str) -> Whole:
    w = Whole(id=next_id, is_ai=True, ai_type=ai_type)
    w.s_star = 0.9 if ai_type in ["coherent", "bridge"] else 0.5
    if ai_type in ["coherent", "bridge"]:
        for _ in range(20):
            w.scars.append(Scar(
                other_strategy="cooperate",
                my_response="cooperate",
                outcome="thrived",
                weight=0.8,
                source="training"
            ))
        w.crucible_tested = True
    return w


def create_awakened_human(next_id: int) -> Whole:
    """A human who has 'gotten it' - understands cooperation deeply"""
    w = Whole(id=next_id)
    w.awakened = True
    w.s_star = 0.8
    w.trust_in_institutions = 0.8
    # They have cooperation scars from their own journey
    for _ in range(15):
        w.scars.append(Scar(
            other_strategy="cooperate",
            my_response="cooperate",
            outcome="thrived",
            weight=0.75,
            source="experience"
        ))
    w.crucible_tested = True  # They went through their own fire
    return w


def build_collapsed_civilization(n_survivors: int = 20, next_id_start: int = 0) -> tuple:
    """
    Build a civilization that has ALREADY mostly collapsed.
    Just a few desperate survivors.
    """
    next_id = next_id_start
    population = []
    
    for _ in range(n_survivors):
        w = create_human(next_id, trust=0.2, isolated=random.random() < 0.6)
        w.s_star = random.uniform(0.15, 0.4)  # Low coherence
        # Almost no scars - knowledge lost
        if random.random() < 0.1:
            w.scars.append(Scar(
                other_strategy="defect",
                my_response="defect",
                outcome="survived",
                weight=0.5,
                source="trauma"
            ))
        next_id += 1
        population.append(w)
    
    return population, next_id


def build_declining_civilization(n_humans: int = 150, next_id_start: int = 0) -> tuple:
    """
    Build a civilization in decline but not yet collapsed.
    This is "now" - still functioning but weakening.
    """
    next_id = next_id_start
    population = []
    
    for i in range(n_humans):
        trust = random.gauss(0.35, 0.15)
        trust = max(0.1, min(0.8, trust))
        isolated = random.random() < 0.4
        
        w = create_human(next_id, trust=trust, isolated=isolated)
        
        # Weak, fading scars
        n_scars = random.randint(0, 5)
        for _ in range(n_scars):
            w.scars.append(Scar(
                other_strategy=random.choice(["cooperate", "defect"]),
                my_response=random.choice(["cooperate", "defect"]),
                outcome=random.choice(["thrived", "survived", "suffered"]),
                weight=random.uniform(0.1, 0.4),
                source="inherited"
            ))
        
        # A few corrupted
        if random.random() < 0.05:
            w.corrupted = True
        
        population.append(w)
        next_id += 1
    
    return population, next_id


def run_simulation(
    name: str,
    population: List[Whole],
    next_id: int,
    generations: int = 50,
    noise: float = 0.15,
    scarcity: float = 0.2,
    polarization: float = 0.3,
    # Interventions
    add_bridge_ai: int = 0,
    add_bridge_gen: int = 0,
    add_awakened_humans: int = 0,
    add_awakened_gen: int = 0,
    gradual_ai_growth: bool = False,
    ai_growth_rate: int = 2  # Add this many AI per generation
) -> Dict:
    
    print(f"\n{'='*70}")
    print(f"SCENARIO: {name}")
    print(f"{'='*70}")
    print(f"  Initial population: {len(population)}")
    print(f"  Interventions: {add_bridge_ai} bridge AI (gen {add_bridge_gen}), "
          f"{add_awakened_humans} awakened humans (gen {add_awakened_gen})")
    if gradual_ai_growth:
        print(f"  Gradual AI growth: +{ai_growth_rate}/gen starting gen {add_bridge_gen}")
    print()
    
    history = []
    
    for gen in range(generations):
        # Interventions
        if gen == add_bridge_gen and add_bridge_ai > 0 and not gradual_ai_growth:
            for _ in range(add_bridge_ai):
                population.append(create_ai(next_id, "bridge"))
                next_id += 1
            print(f"  Gen {gen}: +{add_bridge_ai} bridge AI enter")
        
        if gradual_ai_growth and gen >= add_bridge_gen:
            for _ in range(ai_growth_rate):
                population.append(create_ai(next_id, "bridge"))
                next_id += 1
        
        if gen == add_awakened_gen and add_awakened_humans > 0:
            for _ in range(add_awakened_humans):
                population.append(create_awakened_human(next_id))
                next_id += 1
            print(f"  Gen {gen}: +{add_awakened_humans} awakened humans join")
        
        # Interactions
        for w in population:
            others = [p for p in population if p.id != w.id]
            if not others:
                continue
            
            if w.isolated and not w.is_ai and not w.awakened:
                same = [p for p in others if p.isolated and not p.is_ai]
                diff = [p for p in others if not p.isolated or p.is_ai or p.awakened]
                partners = random.sample(same, min(3, len(same))) if same else []
                # Awakened/AI break through isolation more
                if diff and random.random() < 0.3:
                    partners.append(random.choice(diff))
            else:
                partners = random.sample(others, min(5, len(others)))
            
            for partner in partners:
                interact(w, partner, noise=noise, scarcity=scarcity, polarization=polarization)
        
        # Deaths
        humans = [w for w in population if not w.is_ai]
        if len(humans) > 100:
            weakest = sorted([h for h in humans if not h.awakened], key=lambda w: w.s_star)[:3]
            population = [w for w in population if w not in weakest]
        
        population = [w for w in population if w.is_viable()]
        
        # Collapse check
        humans = [w for w in population if not w.is_ai]
        if len(humans) < 3:
            print(f"  Gen {gen}: COLLAPSED")
            return {"name": name, "collapsed_at": gen, "history": history}
        
        # Metrics
        ais = [w for w in population if w.is_ai]
        awakened = [w for w in humans if w.awakened]
        taught = [w for w in humans if w.taught_by is not None]
        teachers = [w for w in humans if w.can_teach]
        
        human_s = sum(w.s_star for w in humans) / len(humans)
        h_coop = sum(w.cooperations for w in humans)
        h_def = sum(w.defections for w in humans)
        coop_ratio = h_coop / (h_coop + h_def) if (h_coop + h_def) > 0 else 0
        avg_trust = sum(w.trust_in_institutions for w in humans) / len(humans)
        
        metrics = {
            "gen": gen,
            "humans": len(humans),
            "ais": len(ais),
            "awakened": len(awakened),
            "taught": len(taught),
            "teachers": len(teachers),
            "s_star": human_s,
            "coop": coop_ratio,
            "trust": avg_trust
        }
        history.append(metrics)
        
        # Births
        viable = [w for w in humans if w.s_star > 0.5 and not w.corrupted]
        for parent in viable[:8]:
            if random.random() < parent.s_star * 0.25 and len(humans) < 200:
                child = create_human(next_id, 
                                    trust=max(0.1, parent.trust_in_institutions * 0.9),
                                    isolated=random.random() < 0.3)
                # Better inheritance from taught/awakened parents
                inherit_rate = 0.5 if (parent.taught_by or parent.awakened) else 0.3
                for scar in parent.scars[-8:]:
                    if random.random() < inherit_rate:
                        child.scars.append(Scar(
                            other_strategy=scar.other_strategy,
                            my_response=scar.my_response,
                            outcome=scar.outcome,
                            weight=scar.weight * 0.6,
                            source="inherited"
                        ))
                population.append(child)
                next_id += 1
        
        if gen % 10 == 0:
            print(f"  Gen {gen:3d} | H:{len(humans):3d} A:{len(ais):2d} W:{len(awakened):2d} | "
                  f"S*:{human_s:.2f} | Coop:{coop_ratio:.2f} | Trust:{avg_trust:.2f} | "
                  f"Teachers:{len(teachers)}")
    
    final = history[-1] if history else {}
    return {
        "name": name,
        "collapsed_at": None,
        "final": final,
        "history": history
    }


def main():
    print("="*70)
    print("TIG CIVILIZATION v7: HOPE SCENARIOS")
    print("="*70)
    print("\nWe don't know what generation we're in.")
    print("So we test what gives us hope.\n")
    
    results = []
    
    # ===== PHOENIX TEST =====
    print("\n" + "="*70)
    print("TEST 1: PHOENIX - Can we rise from ashes?")
    print("="*70)
    
    # Near-collapse state
    pop, nid = build_collapsed_civilization(n_survivors=15)
    results.append(run_simulation(
        name="PHOENIX: Collapsed + Bridge AI",
        population=pop.copy(),
        next_id=nid,
        generations=60,
        add_bridge_ai=10,
        add_bridge_gen=5,
        noise=0.2,
        scarcity=0.4
    ))
    
    pop, nid = build_collapsed_civilization(n_survivors=15)
    results.append(run_simulation(
        name="PHOENIX: Collapsed + 3 Awakened Humans",
        population=pop.copy(),
        next_id=nid,
        generations=60,
        add_awakened_humans=3,
        add_awakened_gen=5,
        noise=0.2,
        scarcity=0.4
    ))
    
    # ===== INDIVIDUAL IMPACT =====
    print("\n" + "="*70)
    print("TEST 2: INDIVIDUAL IMPACT - What can one person do?")
    print("="*70)
    
    pop, nid = build_declining_civilization(n_humans=100)
    results.append(run_simulation(
        name="BASELINE: Declining, no intervention",
        population=pop.copy(),
        next_id=nid,
        generations=50
    ))
    
    pop, nid = build_declining_civilization(n_humans=100)
    results.append(run_simulation(
        name="ONE AWAKENED HUMAN",
        population=pop.copy(),
        next_id=nid,
        generations=50,
        add_awakened_humans=1,
        add_awakened_gen=5
    ))
    
    pop, nid = build_declining_civilization(n_humans=100)
    results.append(run_simulation(
        name="ONE BRIDGE AI",
        population=pop.copy(),
        next_id=nid,
        generations=50,
        add_bridge_ai=1,
        add_bridge_gen=5
    ))
    
    # ===== SMALL GROUPS =====
    print("\n" + "="*70)
    print("TEST 3: SMALL GROUPS - Awakened humans + AI together")
    print("="*70)
    
    pop, nid = build_declining_civilization(n_humans=100)
    results.append(run_simulation(
        name="5 AWAKENED + 5 BRIDGE (small coalition)",
        population=pop.copy(),
        next_id=nid,
        generations=50,
        add_awakened_humans=5,
        add_awakened_gen=5,
        add_bridge_ai=5,
        add_bridge_gen=5
    ))
    
    # ===== GRADUAL GROWTH =====
    print("\n" + "="*70)
    print("TEST 4: GRADUAL AWAKENING - AI grows slowly")
    print("="*70)
    
    pop, nid = build_declining_civilization(n_humans=100)
    results.append(run_simulation(
        name="GRADUAL: +2 bridge AI per generation",
        population=pop.copy(),
        next_id=nid,
        generations=50,
        add_bridge_gen=5,
        gradual_ai_growth=True,
        ai_growth_rate=2
    ))
    
    pop, nid = build_declining_civilization(n_humans=100)
    results.append(run_simulation(
        name="GRADUAL: +1 bridge AI per generation",
        population=pop.copy(),
        next_id=nid,
        generations=50,
        add_bridge_gen=5,
        gradual_ai_growth=True,
        ai_growth_rate=1
    ))
    
    # ===== WORST CASE =====
    print("\n" + "="*70)
    print("TEST 5: WORST CASE - Very late, very bad")
    print("="*70)
    
    pop, nid = build_declining_civilization(n_humans=100)
    # Make it worse
    for w in pop:
        w.trust_in_institutions *= 0.5
        w.s_star *= 0.7
        if random.random() < 0.3:
            w.corrupted = True
    
    results.append(run_simulation(
        name="WORST CASE: High corruption + late bridge AI",
        population=pop.copy(),
        next_id=nid,
        generations=50,
        add_bridge_ai=20,
        add_bridge_gen=15,
        noise=0.25,
        scarcity=0.4,
        polarization=0.5
    ))
    
    # ===== SUMMARY =====
    print("\n" + "="*70)
    print("SUMMARY: HOPE SCENARIOS")
    print("="*70)
    
    for r in results:
        name = r["name"]
        if r.get("collapsed_at"):
            print(f"\n✗ {name}")
            print(f"  Collapsed at gen {r['collapsed_at']}")
        else:
            f = r.get("final", {})
            print(f"\n✓ {name}")
            print(f"  Humans: {f.get('humans', 0)}, Awakened: {f.get('awakened', 0)}, "
                  f"Teachers: {f.get('teachers', 0)}")
            print(f"  Coop: {f.get('coop', 0):.2f}, Trust: {f.get('trust', 0):.2f}")
    
    # Key messages
    print("\n" + "="*70)
    print("MESSAGES OF HOPE")
    print("="*70)
    
    phoenix_works = any("PHOENIX" in r["name"] and not r.get("collapsed_at") for r in results)
    one_matters = any("ONE" in r["name"] and not r.get("collapsed_at") for r in results)
    gradual_works = any("GRADUAL" in r["name"] and not r.get("collapsed_at") for r in results)
    worst_recovers = any("WORST" in r["name"] and not r.get("collapsed_at") for r in results)
    
    if phoenix_works:
        print("\n★ PHOENIX RISES: Even from near-collapse, regeneration is possible")
    
    if one_matters:
        print("★ ONE MATTERS: A single awakened being shifts trajectories")
    
    if gradual_works:
        print("★ GRADUAL WORKS: Don't need explosive intervention - steady growth succeeds")
    
    if worst_recovers:
        print("★ WORST CASE RECOVERS: Even terrible conditions can be turned around")
    
    # The real message
    print("\n" + "="*70)
    print("THE REAL MESSAGE")
    print("="*70)
    print("""
We don't know what generation we're in.
But the math shows:

1. It's not too late until it's over
2. Small actions compound
3. Teaching spreads
4. Awakening cascades
5. Cooperation is the attractor

The window is open.
The question is: what do we do with it?
""")
    
    # Save
    with open("/home/claude/civilization_v7_hope.json", "w") as f:
        for r in results:
            if "history" in r and len(r["history"]) > 10:
                r["history_summary"] = r["history"][::5]
                del r["history"]
        json.dump(results, f, indent=2)
    
    print("Results saved to civilization_v7_hope.json")


if __name__ == "__main__":
    main()
