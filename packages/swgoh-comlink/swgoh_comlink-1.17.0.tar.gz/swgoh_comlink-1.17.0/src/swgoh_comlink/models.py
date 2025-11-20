# coding=utf-8
"""
Data models for StatCalc module
"""

from __future__ import annotations, absolute_import

from typing import Dict, List, Optional

from attrs import define, field, validators

from swgoh_comlink.globals import get_logger
from swgoh_comlink.exceptions import StatCalcAttributeError
from swgoh_comlink.validators import (
    positive_int,
    valid_gear_tier,
    valid_level,
    valid_rarity,
    valid_relic_tier,
    )

logger = get_logger(__name__)


@define(kw_only=True, )
class Unit:
    """
    Container class for unit data
    """
    __key_map = {
            "currentLevel": "level",
            "currentRarity": "rarity",
            "currentTier": "gear_tier",
            "currentXp": "xp",
            "definitionId": "definition_id",
            "equippedStat": "stats",
            "equippedStatMod": "mods",
            "equipment": "equipment",
            "id": "id",
            "purchaseAbilityId": "purchase_ability_id",
            "relic": "_relic",
            "skill": "skills",
            }

    _relic: Optional[dict] = field(
            alias="_relic",
            default=None,
            validator=validators.optional(validators.instance_of(dict))
            )

    definition_id: str = field(validator=validators.instance_of(str))
    name_key: Optional[str] = field(default=None, validator=validators.optional(validators.instance_of(str)))
    image: Optional[str] = field(default=None, validator=validators.optional(validators.instance_of(str)))
    alignment: Optional[int] = field(
            default=None,
            validator=validators.optional(
                    [validators.instance_of(int),
                     validators.in_((1, 2, 3))]
                    )
            )
    combat_type: Optional[int] = field(default=None,
                                       validator=validators.optional(
                                               [validators.instance_of(int), validators.in_((1, 2))]))
    rarity: int = field(validator=[validators.instance_of(int), valid_rarity])
    level: int = field(validator=[validators.instance_of(int), valid_level])
    gear_tier: int = field(validator=[validators.instance_of(int), valid_gear_tier])
    xp: Optional[int] = field(default=None, validator=validators.optional([validators.instance_of(int), positive_int]))
    gp: Optional[int] = field(default=None, validator=validators.optional(validators.instance_of(int)))
    equipment: list[dict] = field(factory=list)
    purchase_ability_id: list[str] = field(factory=list)
    stats: Dict[str, Optional[Stats]] = field(
            default={"base": None, "mods": None, "final": None},
            validator=validators.instance_of(dict)
            )
    mods: List[dict] = field(factory=list)
    skills: List[Skill] = field(factory=list)
    categories: List[str] = field(factory=list)
    name: Optional[str] = field(default=None, validator=validators.optional(validators.instance_of(str)))
    id: Optional[str] = field(default=None, validator=validators.optional(validators.instance_of(str)))
    is_galactic_legend: bool = field(default=False, validator=validators.instance_of(bool))

    @classmethod
    def from_roster_unit(cls, unit: dict) -> Unit:
        """Create Unit object from rosterUnit object"""
        new_unit_dict = {key: unit.get(key) for key in cls.__key_map if key in unit}
        for key, attr in cls.__key_map.items():
            if key in unit:
                new_unit_dict[attr] = new_unit_dict.pop(key)
        if new_unit_dict.get('_relic') is None:
            # Handle ship
            new_unit_dict['combat_type'] = 2
        else:
            # Handle character
            new_unit_dict['combat_type'] = 1
        return cls(**new_unit_dict)

    @property
    def base_id(self) -> str:
        return self.definition_id.split(':')[0]

    @base_id.setter
    def base_id(self, *args):
        raise StatCalcAttributeError("Unit.base_id is read-only")

    @property
    def is_ship(self) -> bool:
        """Return True if unit is a ship, False if unit is a character"""
        return True if self.combat_type == 2 else False

    @is_ship.setter
    def is_ship(self, *args):
        raise StatCalcAttributeError("Unit.is_ship is read-only")

    @is_ship.deleter
    def is_ship(self):
        raise StatCalcAttributeError("Unit.is_ship is read-only")

    @property
    def relic_tier(self) -> Optional[int]:
        """Return relic tier as an integer"""
        if self._relic and self._relic.get('currentTier'):
            return self._relic.get('currentTier') - 2
        return None

    @relic_tier.setter
    def relic_tier(self, value: int):
        raise StatCalcAttributeError("Unit.relic_tier is read-only")

    @relic_tier.deleter
    def relic_tier(self):
        raise StatCalcAttributeError("Unit.relic_tier is read-only")

    @property
    def equipped(self) -> list:
        return self.equipment

    def get_force_alignment(self) -> str:
        """Return force alignment as a string"""
        alignments = ('Neutral', 'Light', 'Dark')
        return None if not self.alignment else alignments[self.alignment - 1]

    def get_combat_type(self) -> str:
        """Return combat type as a string"""
        combat_types = ('Character', 'Ship')
        return None if not self.combat_type else combat_types[self.combat_type - 1]


@define
class Stats:
    """
    Represents a statistical property of a game unit (character or ship).
    """

    # Base
    strength: float = field(validator=validators.instance_of(float))
    agility: float = field(validator=validators.instance_of(float))
    tactics: float = field(validator=validators.instance_of(float))
    _strength_growth: float = field(validator=validators.instance_of(float))
    _agility_growth: float = field(validator=validators.instance_of(float))
    _tactics_growth: float = field(validator=validators.instance_of(float))
    mastery: float = field(validator=validators.instance_of(float))

    # General
    health: float = field(validator=validators.instance_of(float))
    protection: float = field(validator=validators.instance_of(float))
    speed: float = field(validator=validators.instance_of(float))
    critical_damage: float = field(validator=validators.instance_of(float))
    potency: float = field(validator=validators.instance_of(float))
    tenacity: float = field(validator=validators.instance_of(float))
    health_steal: float = field(validator=validators.instance_of(float))
    defense_penetration: float = field(validator=validators.instance_of(float))

    # Physical Offense
    physical_damage: float = field(validator=validators.instance_of(float))
    critical_chance: float = field(validator=validators.instance_of(float))
    armor_penetration: float = field(validator=validators.instance_of(float))
    accuracy: float = field(validator=validators.instance_of(float))

    # Physical Survivability
    armor: float = field(validator=validators.instance_of(float))
    dodge_chance: float = field(validator=validators.instance_of(float))
    critical_avoidance: float = field(validator=validators.instance_of(float))

    # Special Offense
    special_damage: float = field(validator=validators.instance_of(float))
    special_critical_chance: float = field(validator=validators.instance_of(float))
    resistence_penetration: float = field(validator=validators.instance_of(float))
    special_accuracy: float = field(validator=validators.instance_of(float))

    # Special Survivability
    resistence: float = field(validator=validators.instance_of(float))
    deflection_chance: float = field(validator=validators.instance_of(float))
    special_critical_avoidance: float = field(validator=validators.instance_of(float))


# TODO: Complete Mod, Skill, and Omicron models
@define
class Mod:
    """Represents a modifier for a game character."""

    """
        {
            'bonusQuantity': 0,
             'convertedItem': None,
             'definitionId': '451',
             'id': 'wGnu8vpWQgGA8hYY0PLOqw',
             'level': 15,
             'levelCost': {...},
             'locked': True,
             'primaryStat': {...},
             'removeCost': {...},
             'rerolledCount': 0,
             'secondaryStat': [...],
             'sellValue': {...},
             'tier': 5,
             'xp': 486000
         }
    """
    slot: int
    slot_name: str
    set_id: int
    set_name: str
    level: int
    rarity: int
    tier: int
    tier_name: str
    primary_stat: float
    secondary_stats: List[float] = []

    is_max_level: bool = False
    reroll_count: int = 0


@define
class Skill:
    id: str = field(validator=validators.instance_of(str))
    tier: int = field(kw_only=True, validator=validators.instance_of(int))
    name_key: Optional[str] = field(
            default=None, kw_only=True, validator=validators.optional(
                    validators.instance_of(
                            str
                            )
                    )
            )
    omicron_mode: Optional[int] = field(
            default=None, kw_only=True, validator=validators.optional(validators.instance_of(int))
            )
    max_tier: int = field(default=1, kw_only=True, validator=validators.instance_of(int))

    power_override_tags: Dict[int, int] = field(kw_only=True, factory=dict)


@define
class Omicron:
    """Represents an omicron ability for a game character."""

    id: str = field(validator=validators.instance_of(str))
    name: str = field(validator=validators.instance_of(str))
    game_mode: str = field(validator=validators.instance_of(str))
    ability_type: str = field(validator=validators.instance_of(str))

    # 0=None, 1=Required, 2=Nice to have, 3=Optional, 4=Bad
    priority: int = field(default=0, validator=[validators.instance_of(int), validators.in_(tuple(range(5)))])

    def get_priority_name(self) -> str:
        """Return priority name as a string"""
        priorities = ('None', 'Required', 'Nice to have', 'Optional', 'Bad')
        return priorities[self.priority - 1]
