# coding=utf-8
"""
Python translation of node_modules/swgoh-stat-calc/statCalculator.js

This module mirrors the public API of the JS implementation:
- set_game_data(game_data)
- calc_char_stats(unit, options={}) -> stats dict (and mutates passed unit-like dict with 'stats'/'gp' like JS)
- calc_ship_stats(unit, crew, options={})
- calc_roster_stats(units, options={}) -> count of processed units
- calc_player_stats(players, options={}) -> count
- calc_char_gp(char, options={}) -> int
- calc_ship_gp(ship, crew, options={}) -> int

Notes about inputs:
- The functions accept data in the same shapes as the JS version. Where the JS supports either
  /player.roster objects or /units style objects, this Python code does the same.
- The module expects game data to be provided via set_game_data(game_data) before calculations.

All numeric scaling and math are ported 1:1 from the JS version to preserve parity.
"""
from __future__ import annotations
from typing import Any, List, Tuple, Optional, Union

from swgoh_comlink.globals import get_logger
from swgoh_comlink.constants import DEFAULT_MOD_LEVEL, DEFAULT_MOD_PIPS, DEFAULT_MOD_TIER
from swgoh_comlink.exceptions import StatCalcValueError
from swgoh_comlink.models import Skill, Unit

# Globals
logger = get_logger(__name__)
UNIT_DATA = {}
MOD_SET_DATA = {}
GEAR_DATA = {}
CR_TABLES = {}
GP_TABLES = {}
RELIC_DATA = {}

DEFAULT_OPTIONS = {"calcGP": True, "gameStyle": True}

# A constant holding the mapping between global variable names and their keys in game_data
DATA_MAPPING = {
        'UNIT_DATA': 'unitData',
        'GEAR_DATA': 'gearData',
        'MOD_SET_DATA': 'modSetData',
        'CR_TABLES': 'crTables',
        'GP_TABLES': 'gpTables',
        'RELIC_DATA': 'relicData',
        }


def _update_globals(data_mapping: dict, game_data: dict) -> None:
    """
    Updates the global variables with values from game_data based on the provided mapping.

    Args:
        data_mapping: A dictionary mapping global variable names to keys in game_data.
        game_data: The input dictionary containing all game data.
    """
    globals().update(
            {
                    var_name: game_data.get(data_key, {})
                    for var_name, data_key in data_mapping.items()
                    }
            )


def initialize_game_data(game_data: dict) -> None:
    """
    Initializes global variables with data from the game data dictionary.

    Args:
        game_data: The input dictionary containing all game data.
    """
    _update_globals(DATA_MAPPING, game_data)


def calc_player_stats(players: Union[List[dict], dict[str, Any]],
                      options: Optional[dict] = None) -> Union[List[dict], dict[str, Any]]:
    options = options or DEFAULT_OPTIONS
    if isinstance(players, list):
        for player in players:
            if player.get('rosterUnit'):
                player['rosterUnit'] = calc_roster_stats(player.get('rosterUnit'), options)
    elif isinstance(players, dict):
        if players.get('rosterUnit'):
            players['rosterUnit'] = calc_roster_stats(players.get('rosterUnit'), options)
    else:
        raise ValueError(f"Unexpected type for 'players' argument: {type(players)}")
    return players


def calc_roster_stats(units: List[dict], options: Optional[dict] = None) -> List[Unit]:
    options = options or DEFAULT_OPTIONS
    if not isinstance(units, list):
        raise ValueError(f"Unexpected type for 'units' argument: {type(units)}")

    new_units: List[Unit] = []
    ships: List[Unit] = []
    crew_map: dict[str, Unit] = {}
    # characters first
    for unit in units:
        base_id = get_base_id(unit)
        if not base_id:
            logger.error(f"No base_id for unit. Skipping.")
            continue
        print(f'Unit base_id is {base_id!r} [{unit.get('id')}]')
        if not base_id:
            logger.error(f'Unit has no base_id. Skipping.')
            continue
        game_data_unit = UNIT_DATA.get(base_id)
        if not game_data_unit:
            logger.error(f'Unit {base_id!r} has no entry in DataBuilder unitData. Skipping.')
            continue
        if game_data_unit.get('combatType') == 2:
            ships.append(Unit.from_roster_unit(unit))
        else:
            temp_unit = Unit.from_roster_unit(unit)
            temp_unit.stats = calc_char_stats(temp_unit, options)
            if 'gp' in temp_unit.stats:
                temp_unit.gp = temp_unit.stats.get('gp')
            crew_map[base_id] = temp_unit
            new_units.append(temp_unit)
    # then ships, using crew
    for ship in ships:
        base_id = get_base_id(ship)
        if not base_id:
            logger.error(f'Ship has no base_id. Skipping.')
            continue
        game_data_unit = UNIT_DATA.get(base_id)
        if not game_data_unit:
            logger.error(f'Ship {base_id!r} has no entry in DataBuilder unitData. Skipping.')
            continue
        crw = [crew_map.get(crew_member_base_id) for crew_member_base_id in game_data_unit.get('crew', [])]
        # crw = [c for c in crw if c]
        ship.stats = calc_ship_stats(ship, crw, options)
        if 'gp' in ship.stats:
            ship.gp = ship.stats.get('gp')
        new_units.append(ship)
    return new_units


def calc_char_stats(
        unit: Union[dict, Unit],
        options: Optional[dict] = None
        ) -> dict:
    options = options or DEFAULT_OPTIONS
    char = init_char(unit)
    base_id = get_base_id(char)

    stats = {
            "base": {},
            "mods": {},
            "final": {},
            "gp": None,
            }
    if not options.get('onlyGP'):
        stats = _get_char_raw_stats(char)
        stats = _calculate_base_stats(stats, char.level, base_id)
        stats['mods'] = _calculate_mod_stats(stats['base'], char)
        stats = _format_stats(stats, char.level, options)
        stats = _rename_stats(stats, options)
        unit['stats'] = stats

    if options.get('calcGP') or options.get('onlyGP'):
        unit['gp'] = calc_char_gp(char)
        stats['gp'] = unit['gp']

    return stats


def calc_ship_stats(
        unit: Union[dict, Unit],
        crew_member_list: List[Unit],
        options: Optional[dict] = None
        ) -> dict:
    options = options or DEFAULT_OPTIONS

    ship, crew = init_ship(unit, crew_member_list)

    stats = {"base": {}, "mods": {}, "final": {}}

    if not options.get('onlyGP'):
        stats = _get_ship_raw_stats(ship, crew)
        stats = _calculate_base_stats(stats, ship['level'], ship['defId'])
        stats = _format_stats(stats, ship['level'], options)
        stats = _rename_stats(stats, options)
        unit['stats'] = stats

    if options.get('calcGP') or options.get('onlyGP'):
        unit['gp'] = calc_ship_gp(ship, crew)
        stats['gp'] = unit['gp']

    return stats


# Internals ------------------------------------------------------------------

def get_base_id(unit: Union[dict, Unit]) -> Optional[str]:
    if not isinstance(unit, (dict, Unit)):
        raise StatCalcValueError(f'Unit argument is not a dict or Unit.')
    return_value = None
    if isinstance(unit, dict):
        if 'definitionId' in unit:
            return_value = unit['definitionId'].split(':')[0]
        elif 'baseId' in unit:
            return_value = unit['baseId']
        else:
            raise StatCalcValueError(f'Unit argument does not contain a "baseId" or "definitionId" key.')
    else:
        return_value = unit.base_id
    return return_value


def get_mod_pips(mod_def_id: str) -> Optional[int]:
    return_value = None
    if isinstance(mod_def_id, str):
        return_value = int(mod_def_id[1])


def _get_char_raw_stats(char: Union[dict, Unit]) -> dict:
    if isinstance(char, dict):
        base_id = get_base_id(char)
        rarity = str(char.get('rarity'))
        equipped_gear = char.get('equipped', [])
        relic_tier = char.get('relic', {}).get('currentTier', 0)
    elif isinstance(char, Unit):
        base_id = char.base_id
        rarity = str(char.rarity)
        equipped_gear = char.equipment
        relic_tier = char.relic_tier
    else:
        raise StatCalcValueError(f'Char argument is not a dict or Unit.')

    unit_data_char = UNIT_DATA.get(base_id)
    stats = {
            'base': unit_data_char.get('gearLvl', {}).get(char.get('gear', {})).get('stats', {}),
            'growthModifiers': unit_data_char.get('growthModifiers', {}).get(rarity, {}),
            'gear': {}
            }
    base = stats['base']
    gear_agg = stats['gear']

    # equipped gear stats
    equipment_ids = [gear['equipmentId'] for gear in equipped_gear if 'equipmentId' in gear]
    for equipment_id in equipment_ids:
        gentry = GEAR_DATA.get(equipment_id)
        if not gentry:
            logger.warning(f'No gear data found for equipment ID {equipment_id!r}.')
            continue
        gstats = gentry.get('stats', {})
        for stat_id, stat_value in gstats.items():
            if stat_id in ("2", "3", "4"):
                base[stat_id] = base.get(stat_id, 0.0) + stat_value
            else:
                gear_agg[stat_id] = gear_agg.get(stat_id, 0.0) + stat_value

    # relics
    if relic_tier:
        relic = RELIC_DATA.get(unit_data_char.get('relic', {}).get(str(relic_tier)))
        for stat_id, stat_value in relic['stats'].items():
            base[stat_id] = base.get(stat_id, 0.0) + stat_value
        for stat_id, stat_value in relic['gms'].items():
            stats['growthModifiers'][stat_id] = stats['growthModifiers'].get(stat_id, 0.0) + stat_value

    return stats


def _get_ship_raw_stats(ship: Union[dict, Unit], crew: List[Union[dict, Unit]]) -> dict:
    if isinstance(ship, dict):
        base_id = get_base_id(ship)
        rarity = str(ship.get('rarity'))
    elif isinstance(ship, Unit):
        base_id = ship.base_id
        rarity = str(ship.rarity)
    else:
        raise StatCalcValueError(f'Ship argument is not a dict or Unit.')

    unit_data_ship = UNIT_DATA.get(base_id)

    if len(crew) != len(unit_data_ship.get('crew', [])):
        raise ValueError(f"Incorrect number of crew members ({len(crew)}) for ship {base_id!r}.")

    for c in crew:
        crew_base_id = get_base_id(c)
        if crew_base_id not in unit_data_ship.get('crew', []):
            raise ValueError(f"Unit {crew_base_id!r} is not in {base_id!r}'s crew.")

    crew_rating = _get_crewless_crew_rating(ship) if len(crew) == 0 else _get_crew_rating(crew)

    stats = {
            'base': unit_data_ship.get('stats', {}),
            'crew': {},
            'growthModifiers': unit_data_ship.get('growthModifiers', {}).get(rarity)
            }

    stat_multiplier = CR_TABLES.get('shipRarityFactor', {}).get(rarity, 1.0) * crew_rating

    for stat_id, stat_value in unit_data_ship.get('crewStats', {}).items():
        sid = int(stat_id)
        digits = 8 if (sid < 16 or sid == 28) else 0
        stats['crew'][stat_id] = floor(stat_value * stat_multiplier, digits)

    return stats


def _get_crew_rating(crew: List[Union[dict, Unit]]) -> float:
    total = 0.0
    for char in crew:
        if isinstance(char, dict):
            level = char.get('level')
            rarity = char.get('rarity')
            gear_tier = char.get('gear')
            equipment = char.get('equipped', [])
        elif isinstance(char, Unit):
            level = char.level
            rarity = char.rarity
            gear_tier = char.gear_tier
            equipment = char.equipment
        else:
            raise StatCalcValueError(f'Crew argument is not a dict or Unit.')

        total += CR_TABLES.get('unitLevelCR', {}).get(level) + CR_TABLES.get('crewRarityCR', {}).get(rarity, 0.0)
        total += CR_TABLES.get('gearLevelCR', {}).get(gear_tier, 0.0)
        total += CR_TABLES.get('gearPieceCR', {}).get(gear_tier, 0.0) * len(equipment)

        # abilities
        for skill in char.get('skills', []) or []:
            total += _get_skill_crew_rating(skill)

        # mods
        if isinstance(char, dict):
            for mod in char['mods']:
                total += CR_TABLES.get('modRarityLevelCR', {})[mod['pips']][mod['level']]
        elif isinstance(char, Unit):
            for mod in char.mods:
                total += CR_TABLES.get('modRarityLevelCR', {})[int(mod['definitionId'][1])][mod['level']]

        # relics
        if char.get('relic') and char.get('relic', {}).get('currentTier', 0) > 2:
            total += CR_TABLES['relicTierCR'][char.get('relic', {}).get('currentTier') - 2] or 0.0
            total += (char['level']
                      * CR_TABLES['relicTierLevelFactor'].get(char.get('relic', {}).get('currentTier') - 2, 0.0))
    return total


def _get_skill_crew_rating(skill: dict) -> float:
    return CR_TABLES['abilityLevelCR'][skill['tier']]


def _get_crewless_crew_rating(ship: dict) -> float:
    return floor(
            CR_TABLES['crewRarityCR'][ship['rarity']] + 3.5 * CR_TABLES['unitLevelCR'][ship['level']]
            + _get_crewless_skills_crew_rating(ship.get('skills', []) or [])
            )


def _get_crewless_skills_crew_rating(skills: List[dict]) -> float:
    cr = 0.0
    for skill in skills:
        # hardware vs regular
        mult = 0.696 if skill['id'][:8] == 'hardware' else 2.46
        cr += mult * CR_TABLES['abilityLevelCR'][skill['tier']]
    return cr


def _calculate_base_stats(stats: dict[str, dict], level: int, base_id: str) -> dict:
    # growth modifiers to primaries
    stats['base'][2] = stats['base'].setdefault(2, 0) + floor(stats['growthModifiers'][2] * level, 8)
    stats['base'][3] = stats['base'].setdefault(3, 0) + floor(stats['growthModifiers'][3] * level, 8)
    stats['base'][4] = stats['base'].setdefault(4, 0) + floor(stats['growthModifiers'][4] * level, 8)

    ud = UNIT_DATA[base_id]
    if stats['base'].get(61):
        mms = CR_TABLES[ud['masteryModifierID']]
        for statID, mult in mms.items():
            sid = int(statID)
            stats['base'][sid] = stats['base'].get(sid, 0) + stats['base'][61] * mult

    # primary effects -> secondary
    stats['base'][1] = stats['base'].get(1, 0) + stats['base'][2] * 18
    stats['base'][6] = floor(stats['base'].get(6, 0) + stats['base'][ud['primaryStat']] * 1.4, 8)
    stats['base'][7] = floor(stats['base'].get(7, 0) + (stats['base'][4] * 2.4), 8)
    stats['base'][8] = floor(stats['base'].get(8, 0) + (stats['base'][2] * 0.14) + (stats['base'][3] * 0.07), 8)
    stats['base'][9] = floor(stats['base'].get(9, 0) + (stats['base'][4] * 0.1), 8)
    stats['base'][14] = floor(stats['base'].get(14, 0) + (stats['base'][3] * 0.4), 8)

    # minimums / defaults
    stats['base'][12] = stats['base'].get(12, 0) + (24 * 1e8)
    stats['base'][13] = stats['base'].get(13, 0) + (24 * 1e8)
    stats['base'][15] = stats['base'].get(15, 0)
    stats['base'][16] = stats['base'].get(16, 0) + (150 * 1e6)
    stats['base'][18] = stats['base'].get(18, 0) + (15 * 1e6)

    return stats


def _calculate_mod_stats(base_stats: dict, char: dict) -> dict:
    if not char.get('mods') and not char.get('equippedStatMod'):
        return {}

    set_bonuses = {}
    raw_mod_stats = {}

    if char.get('mods'):
        for mod in char['mods']:
            if not mod.get('set'):
                continue
            sid = mod['set']
            if sid in set_bonuses:
                set_bonuses[sid]['count'] += 1
                if mod.get('level') == 15:
                    set_bonuses[sid]['maxLevel'] += 1
            else:
                set_bonuses[sid] = {'count': 1, 'maxLevel': 1 if mod.get('level') == 15 else 0}

            if mod.get('stat'):
                for s in mod['stat']:
                    stat_id, stat_val = int(s[0]), s[1]
                    raw_mod_stats[stat_id] = raw_mod_stats.get(stat_id, 0) + _scale_mod_stat_value(stat_id, stat_val)
            else:
                # /player.roster
                stat = mod['primaryStat']
                i = 0
                while True:
                    raw_mod_stats[stat['unitStat']] = raw_mod_stats.get(stat['unitStat'], 0) + _scale_mod_stat_value(
                            stat['unitStat'], stat['value']
                            )
                    if i >= len(mod.get('secondaryStat', [])):
                        break
                    stat = mod['secondaryStat'][i]
                    i += 1
    elif char.get('equippedStatMod'):
        for mod in char['equippedStatMod']:
            set_id = int(mod['definitionId'][0])
            sb = set_bonuses.get(set_id)
            if sb:
                sb['count'] += 1
                if mod.get('level') == 15:
                    sb['maxLevel'] += 1
            else:
                set_bonuses[set_id] = {'count': 1, 'maxLevel': 1 if mod.get('level') == 15 else 0}
            stat = mod['primaryStat']['stat']
            i = 0
            while True:
                raw_mod_stats[stat['unitStatId']] = float(stat['unscaledDecimalValue']) + raw_mod_stats.get(
                        stat['unitStatId'], 0
                        )
                if i >= len(mod.get('secondaryStat', [])):
                    break
                sec = mod['secondaryStat'][i]
                stat = sec.get('stat') if sec else None
                i += 1
                if not stat:
                    break

    # set bonuses
    for set_id, sb in list(set_bonuses.items()):
        set_def = MOD_SET_DATA[str(set_id)] if str(set_id) in MOD_SET_DATA else MOD_SET_DATA.get(str(set_id))
        if not set_def:
            continue
        count = sb['count']
        max_count = sb['maxLevel']
        multiplier = (count // set_def['count']) + (max_count // set_def['count'])
        bonus_stat_id = int(set_def['id'])
        raw_mod_stats[bonus_stat_id] = raw_mod_stats.get(bonus_stat_id, 0) + (set_def['value'] * multiplier)

    # compute final mod contributions
    mod_stats = {}
    for statID_raw, value in raw_mod_stats.items():
        stat_id = int(statID_raw)
        if stat_id == 41:  # Offense
            mod_stats[6] = mod_stats.get(6, 0) + value
            mod_stats[7] = mod_stats.get(7, 0) + value
        elif stat_id == 42:  # Defense
            mod_stats[8] = mod_stats.get(8, 0) + value
            mod_stats[9] = mod_stats.get(9, 0) + value
        elif stat_id == 48:  # Offense %
            mod_stats[6] = floor(mod_stats.get(6, 0) + (base_stats.get(6, 0) * 1e-8 * value), 8)
            mod_stats[7] = floor(mod_stats.get(7, 0) + (base_stats.get(7, 0) * 1e-8 * value), 8)
        elif stat_id == 49:  # Defense %
            mod_stats[8] = floor(mod_stats.get(8, 0) + (base_stats.get(8, 0) * 1e-8 * value), 8)
            mod_stats[9] = floor(mod_stats.get(9, 0) + (base_stats.get(9, 0) * 1e-8 * value), 8)
        elif stat_id == 53:  # Crit Chance
            mod_stats[21] = mod_stats.get(21, 0) + value
            mod_stats[22] = mod_stats.get(22, 0) + value
        elif stat_id == 54:  # Crit Avoid
            mod_stats[35] = mod_stats.get(35, 0) + value
            mod_stats[36] = mod_stats.get(36, 0) + value
        elif stat_id == 55:  # Health %
            mod_stats[1] = floor(mod_stats.get(1, 0) + (base_stats.get(1, 0) * 1e-8 * value), 8)
        elif stat_id == 56:  # Protection %
            mod_stats[28] = floor(mod_stats.get(28, 0) + (base_stats.get(28, 0) * 1e-8 * value), 8)
        elif stat_id == 57:  # Speed %
            mod_stats[5] = floor(mod_stats.get(5, 0) + (base_stats.get(5, 0) * 1e-8 * value), 8)
        else:
            mod_stats[stat_id] = mod_stats.get(stat_id, 0) + value
    return mod_stats


def _scale_mod_stat_value(stat_id: int, value: float) -> float:
    # convert displayed value to unscaled value used in calculations
    if stat_id in (1, 5, 28, 41, 42):
        return value * 1e8  # flat
    else:
        return value * 1e6  # percent


def _format_stats(stats: dict, level: int, options: dict) -> dict:
    scale = 1.0
    if options.get('scaled'):
        scale = 1e-4
    elif not options.get('unscaled'):
        scale = 1e-8

    if stats.get('mods'):
        for k in list(stats['mods'].keys()):
            stats['mods'][k] = round(stats['mods'][k])

    if scale != 1.0:
        for k in list(stats.get('base', {}).keys()):
            stats['base'][k] *= scale
        for k in list(stats.get('gear', {}).keys()):
            stats['gear'][k] *= scale
        for k in list(stats.get('crew', {}).keys()):
            stats['crew'][k] *= scale
        for k in list(stats.get('growthModifiers', {}).keys()):
            stats['growthModifiers'][k] *= scale
        if stats.get('mods'):
            for k in list(stats['mods'].keys()):
                stats['mods'][k] *= scale

    if options.get('percentVals') or options.get('gameStyle'):
        def convert_percent(stat_id: int, convert_func):
            flat = stats['base'].get(stat_id)
            if flat is None:
                return
            percent = convert_func(flat)
            stats['base'][stat_id] = percent
            last = percent
            if stats.get('crew') is not None and 'crew' in stats and stats['crew']:
                if stat_id in stats['crew']:
                    stats['crew'][stat_id] = convert_func(flat + stats['crew'][stat_id]) - last
            else:
                if stats.get('gear') and stat_id in stats['gear']:
                    p = convert_func(flat + stats['gear'][stat_id])
                    stats['gear'][stat_id] = p - last
                    last = p
                if stats.get('mods') and stat_id in stats['mods']:
                    stats['mods'][stat_id] = convert_func(flat + stats['mods'][stat_id]) - last

        s = scale * 1e8
        convert_percent(14, lambda v: convert_flat_crit_to_percent(v, s))
        convert_percent(15, lambda v: convert_flat_crit_to_percent(v, s))
        convert_percent(
                8, lambda v: convert_flat_def_to_percent(
                        v, level, s,
                        True if stats.get('crew') is not None and 'crew' in stats and stats['crew'] else False
                        )
                )
        convert_percent(
                9, lambda v: convert_flat_def_to_percent(
                        v, level, s,
                        True if stats.get('crew') is not None and 'crew' in stats and stats['crew'] else False
                        )
                )
        convert_percent(37, lambda v: convert_flat_acc_to_percent(v, s))
        convert_percent(38, lambda v: convert_flat_acc_to_percent(v, s))
        convert_percent(12, lambda v: convert_flat_acc_to_percent(v, s))
        convert_percent(13, lambda v: convert_flat_acc_to_percent(v, s))
        convert_percent(39, lambda v: convert_flat_crit_avoid_to_percent(v, s))
        convert_percent(40, lambda v: convert_flat_crit_avoid_to_percent(v, s))

    if options.get('gameStyle'):
        gs = {'final': {}}
        stat_list = list(stats.get('base', {}).keys())

        def add_stat(stat_list_id):
            if stat_list_id not in stat_list:
                stat_list.append(stat_list_id)

        if stats.get('gear') is not None and 'gear' in stats:
            for sid in stats.get('gear', {}).keys():
                add_stat(sid)
            if stats.get('mods'):
                for sid in stats['mods'].keys():
                    add_stat(sid)
            if stats.get('mods'):
                gs['mods'] = stats['mods']
            for sid in stat_list:
                flat_sid = sid
                if sid in (21, 22):
                    flat_sid = sid - 7
                elif sid in (35, 36):
                    flat_sid = sid + 4
                gs['final'][flat_sid] = (gs['final'].get(flat_sid, 0)
                                         + (stats['base'].get(sid, 0)
                                            + stats.get('gear', {}).get(sid, 0)
                                            + (stats.get('mods', {}).get(sid, 0)
                                               if stats.get('mods') else 0)))
        else:
            for sid in stats.get('crew', {}).keys():
                add_stat(sid)
            gs['crew'] = stats.get('crew', {})
            for sid in stat_list:
                gs['final'][sid] = (stats['base'].get(sid, 0) + stats.get('crew', {}).get(sid, 0))
        stats = gs

    return stats


def _rename_stats(stats: dict, options: dict) -> dict:
    if options.get('language'):
        rn = {}
        for statType, obj in stats.items():
            rn[statType] = {}
            if not isinstance(obj, dict):
                rn[statType] = obj
                continue
            for statID, val in obj.items():
                key = options['language'].get(statID, statID)
                if options.get('noSpace') and isinstance(key, str):
                    key = key.replace(' ', '')
                    key = key[:1].lower() + key[1:]
                rn[statType][key] = val
        stats = rn
    return stats


# GP calculations -------------------------------------------------------------

def calc_char_gp(char: dict) -> int:
    gp: int = GP_TABLES.get('unitLevelGP', {}).get(char.get('level'), 0)
    gp += GP_TABLES.get('unitRarityGP', {}).get(char.get('rarity'), {})
    gp += GP_TABLES.get('gearLevelGP', {}).get(char.get('gear'), {})
    # per-slot piece gp
    gp += sum(GP_TABLES['gearPieceGP'][char['gear']][piece.get('slot')] for piece in (char.get('equipped', [])))

    for skill in char.get('skills', []):
        gp += get_skill_gp(char['defId'], skill)

    if char.get('purchasedAbilityId'):
        gp += len(char['purchasedAbilityId']) * GP_TABLES.get('abilitySpecialGP').get('ultimate', 0.0)

    if char.get('mods'):
        for mod in char['mods']:
            gp += GP_TABLES['modRarityLevelTierGP'][mod['pips']][mod['level']][mod['tier']]
    elif char.get('equippedStatMod'):
        for mod in char['equippedStatMod']:
            gp += GP_TABLES['modRarityLevelTierGP'][int(mod['definitionId'][1])][mod['level']][mod['tier']]

    if char.get('relic') and char['relic'].get('currentTier', 0) > 2:
        relic_tier = char.get('relic', {}).get('currentTier', 2) - 2
        gp += GP_TABLES.get('relicTierGP', {}).get(relic_tier, 0)
        gp += char.get('level', 0.0) * GP_TABLES.get('relicTierLevelFactor', {}).get(relic_tier, 0)
    return int(floor(gp * 1.5))


def get_skill_gp(unit_id: str, skill: dict) -> int:
    o_tag = None
    for s in UNIT_DATA[unit_id].get('skills', []):
        if s.get('id') == skill.get('id'):
            o_tag = s.get('powerOverrideTags', {}).get(skill.get('tier'), None)
            break
    if o_tag:
        return GP_TABLES['abilitySpecialGP'][o_tag]
    else:
        return GP_TABLES['abilityLevelGP'].get(skill.get('tier'), 0)


def calc_ship_gp(
        ship: Union[dict, Unit],
        crew_unit_list: Optional[List[Union[dict, Unit]]] = None
        ) -> int:

    crew_unit_list = crew_unit_list or []

    base_id = get_base_id(ship)

    if not base_id:
        raise ValueError(f"Unable to determine ship base_id.")

    unit_data_ship = UNIT_DATA.get(base_id)

    if len(crew_unit_list) != len(unit_data_ship.get('crew', [])):
        raise ValueError(f"Incorrect number of crew members for ship {base_id}.")

    for crew_unit in crew_unit_list:
        crew_unit_base_id = get_base_id(crew_unit)
        if crew_unit_base_id not in unit_data_ship.get('crew', []):
            raise ValueError(f"Unit {crew_unit_base_id} is not in {base_id}'s crew.")

    if len(crew_unit_list) == 0:
        gps = get_crewless_skills_gp(base_id, ship.skills)
        level_gp = GP_TABLES['unitLevelGP'][ship['level']]
        gp = (level_gp * 3.5 + gps['ability'] * 5.74 + gps['reinforcement'] * 1.61) * GP_TABLES['shipRarityFactor'][
            ship['rarity']]
        gp += level_gp + gps['ability'] + gps['reinforcement']
    else:
        gp = sum(c.get('gp', 0) for c in crew_unit_list)
        gp *= GP_TABLES['shipRarityFactor'][ship['rarity']] * GP_TABLES['crewSizeFactor'][len(crew_unit_list)]
        gp += GP_TABLES['unitLevelGP'][ship['level']]
        for skill in ship.get('skills', []) or []:
            gp += get_skill_gp(ship['defId'], skill)
    return int(floor(gp * 1.5))


def get_crewless_skills_gp(unit_id: str, skills: List[Skill]) -> dict:
    a = 0.0
    r = 0.0
    for skill in skills:
        o_tag = None
        skill_tier = str(skill.tier)
        for unit_skill in UNIT_DATA[unit_id].get('skills', []):
            if skill.id == unit_skill.get('id'):
                o_tag = skill.power_override_tags.get(skill_tier)
                break
        if o_tag and str(o_tag).startswith('reinforcement'):
            r += GP_TABLES['abilitySpecialGP'][o_tag]
        else:
            a += GP_TABLES['abilitySpecialGP'][o_tag] if o_tag else GP_TABLES['abilityLevelGP'][skill['tier']]
    return {'ability': a, 'reinforcement': r}


# Helpers --------------------------------------------------------------------

def floor(value: float, digits: int = 0) -> float:
    # floor to a specified digit power-of-ten scale
    scale = float(f"1e{digits}")
    return int(value / scale) * scale


# conversions

def convert_flat_def_to_percent(value: float, level: int = 85, scale: float = 1.0, is_ship: bool = False) -> float:
    val = value / scale
    level_effect = (300 + level * 5) if is_ship else (level * 7.5)
    return (val / (level_effect + val)) * scale


def convert_flat_crit_to_percent(value: float, scale: float = 1.0) -> float:
    val = value / scale
    return (val / 2400.0 + 0.1) * scale


def convert_flat_acc_to_percent(value: float, scale: float = 1.0) -> float:
    val = value / scale
    return (val / 1200.0) * scale


def convert_flat_crit_avoid_to_percent(value: float, scale: float = 1.0) -> float:
    val = value / scale
    return (val / 2400.0) * scale


# useValues shims -------------------------------------------------------------

def init_char(char: Union[dict, Unit]) -> Unit:
    return char if isinstance(char, Unit) else Unit.from_roster_unit(char)


def init_ship(ship: dict,
              crew: List[Union[dict, Unit]],
              ) -> Tuple[Unit, List[Unit]]:
    new_crew = []

    if isinstance(ship, dict):
        ship = Unit.from_roster_unit(ship)
        for crew_member in crew:
            if isinstance(crew_member, dict):
                new_crew.append(Unit.from_roster_unit(crew_member))
            elif isinstance(crew_member, Unit):
                new_crew.append(crew_member)
            else:
                raise ValueError(f"Invalid crew member: {crew_member}")
            new_crew.append(crew_member)

    return ship, new_crew


def set_skills(unit_id: str, val: Any):
    if val == 'max':
        return [{'id': s['id'], 'tier': s['maxTier']} for s in UNIT_DATA[unit_id]['skills']]
    elif val == 'maxNoZeta':
        return [{'id': s['id'], 'tier': s['maxTier'] - (1 if s.get('isZeta') else 0)} for s in
                UNIT_DATA[unit_id]['skills']]
    elif isinstance(val, int):
        return [{'id': s['id'], 'tier': min(val, s['maxTier'])} for s in UNIT_DATA[unit_id]['skills']]
    else:
        return val
