"""Shared calculators for Clan recruitment and diplomacy"""

def get_outsider_acceptance_chance(clan):
    """Calculate a Clan's chance of accepting a newcomer"""

    chance = 50

    # Adult personality traits
    personality_modifiers = {
        "troublesome": -5,
        "lonesome": -10,
        "fierce": -10,
        "bloodthirsty": -15,
        "cold": -15,
        "childish": 0,
        "playful": 5,
        "charismatic": 10,
        "bold": 5,
        "daring": 5,
        "nervous": -10,
        "righteous": 0,
        "insecure": -10,
        "strict": -10,
        "compassionate": 15,
        "thoughtful": 10,
        "ambitious": -5,
        "confident": 5,
        "adventurous": 10,
        "calm": 5,
        "careful": -5,
        "faithful": 5,
        "loving": 15,
        "loyal": 5,
        "responsible": 5,
        "shameless": -5,
        "strange": 0,
        "vengeful": -15,
        "wise": 10,
        "arrogant": -10,
        "competitive": -5,
        "grumpy": -5,
        "cunning": -10,
        "oblivious": 0,
        "gloomy": -5,
        "sincere": 10,
        "flamboyant": 5,
        "rebellious": 5,
    }

    # clan temperaments
    temperament_modifiers = {
        "cunning": -10,
        "proud": -10,
        "bloodthirsty": -10,
        "amiable": 10,
        "stoic": 0,
        "wary": -10,
        "gracious": 10,
        "mellow": 10,
        "logical": 0,
        "chaotic": 0,
        "mercurial": -5,
        "calculating": -5,
        "eager": 10,
        "observant": 0,
        "adaptable": 10,
        "decisive": 0,
        "methodical": 0,
        "steadfast": 0,
    }

    # Apply the leader's personality modifier.
    if clan.leader:
        trait = clan.leader.personality.trait
        chance += personality_modifiers.get(trait, 0)

    # Apply both Clan temperament modifiers.
    for temperament in clan.temperament:
        chance += temperament_modifiers.get(temperament, 0)

    # Both acceptance and rejection remain possible.
    return max(5, min(95, chance))

def get_defection_relation_penalty(clan):
    """Calculate how negatively a Clan reacts to losing a member"""

    temperament_penalties = {
        "cunning": 4,
        "proud": 5,
        "bloodthirsty": 5,
        "amiable": 1,
        "stoic": 3,
        "wary": 4,
        "gracious": 1,
        "mellow": 1,
        "logical": 2,
        "chaotic": 2,
        "mercurial": 4,
        "calculating": 3,
        "eager": 2,
        "observant": 2,
        "adaptable": 1,
        "decisive": 3,
        "methodical": 2,
        "steadfast": 4,
    }

    penalty = sum(
        temperament_penalties.get(temperament, 2)
        for temperament in clan.temperament
    )

    return -min(10, penalty)
