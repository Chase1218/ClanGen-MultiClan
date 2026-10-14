"""All events with a connection to outsiders."""

import random

from typing import TYPE_CHECKING

import i18n

from scripts.cat.enums import CatGroup
from scripts.clan_package.settings import get_clan_setting
from scripts.events_module.event_information import EventInformation
from scripts.game_structure import game
from scripts.game_structure.localization import load_lang_resource
from scripts.events_module.short.short_event_generation import generate_event_objects
from scripts.events_module.text_adjust import event_text_adjust
from scripts.cat.cats import Cat

# ---------------------------------------------------------------------------- #
#                               New Cat Event Class                              #
# ---------------------------------------------------------------------------- #


def killing_outsiders(cat: "Cat"):
    if info_dict := get_clan_setting("lead_den_outsider_event"):
        if cat.ID == info_dict["cat_ID"]:
            return

    deaths = load_lang_resource("events/death/outsider_deaths/outsider_deaths.json")

    # killing outside cats
    if random.getrandbits(6) == 1 and not cat.dead:
        death_history = i18n.t("events.death.outsider_deaths.history.default")

        if cat.status.is_exiled(CatGroup.PLAYER_CLAN_ID):
            text = random.choice(deaths["exiled"])
            death_history = i18n.t("events.death.outsider_deaths.history.exiled")
        elif cat.status.is_lost(CatGroup.PLAYER_CLAN_ID):
            text = random.choice(deaths["lost"])
            death_history = i18n.t("events.death.outsider_deaths.history.lost")
        elif cat.status.is_other_clancat or (
            cat.status.is_former_clancat
            and not cat.status.get_last_valid_group_id() == CatGroup.PLAYER_CLAN_ID
        ):
            group_id = cat.status.get_last_valid_group_id()
            if cat.status.is_exiled(group_id):
                text = random.choice(deaths["other_clan_exiled"])
                death_history = i18n.t(
                    "events.death.outsider_deaths.history.other_clan_exiled"
                )
            elif cat.status.is_lost(group_id):
                text = random.choice(deaths["other_clan_lost"])
                death_history = i18n.t(
                    "events.death.outsider_deaths.history.other_clan_lost"
                )
            else:
                text = random.choice(deaths["other_clan"])
                death_history = i18n.t(
                    "events.death.outsider_deaths.history.other_clan"
                )

            clanname = [c for c in game.clan.all_other_clans if c.group_ID == group_id][
                0
            ].name
            text = text.replace("o_c_n", clanname)
            death_history = death_history.replace("o_c_n", clanname)
        elif cat.status.is_outsider:
            text = random.choice(deaths[cat.status.social.value])
            death_history = i18n.t(
                f"events.death.outsider_deaths.history.{cat.status.social.value}"
            )
        else:
            text = random.choice(deaths["default"])

        cat.history.add_death(death_text=death_history)
        cat.die(grief_allowed=False)
        if cat.status.is_other_clancat:
            game.cur_events_list.append(
                EventInformation(
                    text, ["birth_death", "other_clans"], cat_dict={"m_c": cat}
                )
            )
        else:
            game.cur_events_list.append(
                EventInformation(text, ["birth_death"], cat_dict={"m_c": cat})
            )
def find_outsider_family_candidates(clan):
    """Find outsiders with young kits and a parent in the Clan."""
    candidates = []

    for outsider in Cat.all_cats.values():
        if outsider.dead or not outsider.status.is_outsider:
            continue

        for child_id in outsider.get_children():
            child = Cat.all_cats.get(child_id)

            if not child or child.dead or child.moons >= 12:
                continue

            # Only biological parents count.
            if outsider.ID not in (child.parent1, child.parent2):
                continue

            other_parent_id = (
                child.parent2
                if child.parent1 == outsider.ID
                else child.parent1
            )
            clan_parent = Cat.all_cats.get(other_parent_id)

            if (
                clan_parent
                and not clan_parent.dead
                and clan_parent.status.is_clancat
                and clan_parent.status.group_ID == clan.group_ID
            ):
                candidates.append((outsider, clan_parent, child))
                break

    return candidates

def roll_outsider_family_arrival(clan):
    """Occasionally select an outsider family seeking to join the Clan."""
    candidates = find_outsider_family_candidates(clan)

    if not candidates:
        return None

    # 1 in 40 chance per Clan per moon when eligible families exist.
    if random.randrange(40) != 0:
        return None

    return random.choice(candidates)

def get_outsider_recruitment_event():
    """Select an event from the outsider recruitment JSON."""
    events = generate_event_objects(
        "outsider_recruitment",
        "general",
        4,
    )

    if not events:
        return None

    return random.choice(events)

def get_outsider_acceptance_chance(clan):
    """Calculate a Clan's chance of accepting a newcomer."""

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


def handle_outsider_family_arrival(clan):
    """Generate an outsider family reunion event for this Clan."""
    family = roll_outsider_family_arrival(clan)

    if not family:
        return

    event = get_outsider_recruitment_event()

    if not event:
        return

    outsider, clan_parent, kit = family
    family_kit_ids = [
        child.ID
        for child_id in outsider.get_children()
        if (child := Cat.all_cats.get(child_id))
        and not child.dead
        and child.moons < 12
        and outsider.ID in (child.parent1, child.parent2)
        and clan_parent.ID in (child.parent1, child.parent2)
    ]

    # Reveal the Clan parent's identity to all eligible kits.
    for kit_id in family_kit_ids:
        child = Cat.all_cats.get(kit_id)
        if child:
            child.reveal_biological_parent(clan_parent)

    event_text = event_text_adjust(
        Cat,
        event.text,
        main_cat=outsider,
        random_cat=clan_parent,
        clan=clan,
    )

    game.cur_events_list.append(
        EventInformation(
            event_text,
            ["misc"],
            [outsider.ID, clan_parent.ID] + family_kit_ids,
            clan=clan.group_ID,
        )
    )
