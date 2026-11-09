# Game parameters of the two challenge conditions

Values are transcribed from the game build specification used in the study. Times are in seconds unless stated otherwise.

## 1. Rule-based condition

### Boss parameters by level

| Boss level | HP phase 1 | HP phase 2 | Chill time (wait before attacking) | Stun chance | Stun cooldown |
|---|---|---|---|---|---|
| 1 | 1,000 | 1,200 | 3.5 | 45% | 4 |
| 2 | 1,200 | 1,500 | 2.8 | 38% | 5 |
| 3 | 1,400 | 1,700 | 2.0 | 30% | 6 |
| 4 | 1,600 | 1,900 | 1.3 | 18% | 7 |
| 5 | 1,800 | 2,200 | 0.8 | 8% | 9 |

Winning an encounter advances the boss level. Every participant started at boss level 1. A play session lasted at most 15 min, and testers could stop at any time.

### Boss skill damage

| Skill | Damage |
|---|---|
| Skill 1: Earth Shatter / Shock | 400 |
| Skill 2: Spell | 350 |
| Skill 3: Swords falling from the sky | 0.6 per sword |
| Skill 4: Scream | 100, 200, 250, or 300 depending on boss level and the part of the skill that hits; may hit more than once per cast (no random damage or hit count) |
| Skill 5: Aura Magic | No damage; stops player movement |

The boss has no defense.

### Player attacks and statistics (fixed during play)

| Attack / skill | Base damage |
|---|---|
| Normal attack | 10–25 depending on the move, increased by ATK |
| Q – Sword Combo | 150 per hit, up to 3 hits (as specified in the build document) |
| E – Fireball | 250 per cast |
| T – Invulnerability | No damage; invulnerable for 2 s |

| Statistic | Value |
|---|---|
| HP | 4,500 |
| Level | 4 |
| ATK | 0 (= 15 damage) |
| DEF | 0 |
| Speed | 5 |
| Luck | 0 |

## 2. Adaptive (time-based) condition

### Starting values (new session: Score = 0, lvF = 0, L_base = 1, t = 0)

| Side | Item | Start value |
|---|---|---|
| Player | Level | 1 |
| Player | Max HP | 350 |
| Player | ATK | 10 |
| Player | DEF | 5 |
| Player | LUCK | 0 |
| Boss | L_base | 1 |
| Boss | Max HP | 500 |
| Boss | Damage multiplier | 1 |
| Boss | GreatSword base damage | 100 |
| Boss | Kick (L_foot) base damage | 6 |
| Boss | Phase 2 | off |

### Boss scaling with time (t = elapsed time in seconds)

| Quantity | Formula |
|---|---|
| Damage multiplier | M(t) = base(L_base) × 1.12^(t/60) |
| Level bonus | base(L_base) = 1 + 0.05 × (L_base − 1) |
| Damage per hit | DMG(t) = D0 × M(t), D0 = base damage of the move |
| Boss max HP | HP = 500 × 1.10^(L_base − 1) |
| Wait before attacking | max(3 − 0.18 × (t/60), 1.2) |
| Animation speed | min(1 + 0.03 × (t/60), 1.5) |
| Lethal rule | at 900 s (15 min) of real session time, any damage that passes the HP system is lethal |
| Effective level (display and telemetry only) | L_effective = L_base + floor(t/60) |

Winning increases L_base by 1 (no cap); losing keeps L_base.

### Player score and statistics

| Item | Formula |
|---|---|
| Score from damage | ΔScore = 50 × ΔDamage / HP_boss,max |
| Score from time | ΔScore = 2 × Time.deltaTime while both characters are alive |
| Fractional level | lvF = max(Score / 100, 0) |
| Level | 1 + floor(lvF) |
| Max HP | round(350 + 60 × lvF) |
| ATK | round(10 + 20 × lvF) |
| DEF | round(5 + 8 × lvF) |
| LUCK | min(round(lvF), 100) |

### Player skills

| Skill | Damage | Cooldown |
|---|---|---|
| Q – Sword Combo | 55 × (1 + ATK/100) per hit, up to 3 hits 1 s apart | 8 |
| E – Fireball | 95 × (1 + ATK/100) per successful hit | 12 |
| T – Invulnerability | No damage; invulnerable for 2 s | 20 |

Normal attacks: D = D0 × (1 + ATK/100), D0 = 10–25 depending on the combo step; critical chance = LUCK/100, critical multiplier 1.5.

### Damage received by the player

D_received = max(0.1 × D_raw, D_raw − DEF), applied before the lethal rule.
