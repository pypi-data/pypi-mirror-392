# coding=utf-8
"""
Attribute validation functions
"""
from __future__ import annotations

from swgoh_comlink.exceptions import ComlinkValueError, StatCalcValueError


# Validator functions
def valid_level(_, attribute, value):
    if value < 1 or value > 85:
        raise ComlinkValueError(f"Level must be between 1 and 85 inclusive.")


def valid_rarity(_, attribute, value):
    if value < 1 or value > 7:
        raise ComlinkValueError(f"Rarity must be between 1 and 7 inclusive.")


def valid_gear_tier(_, attribute, value):
    if value < 1 or value > 13:
        raise ComlinkValueError(f"Gear tier must be between 1 and 13 inclusive.")


def valid_relic_tier(_, attribute, value):
    if value < 1 or value > 9:
        raise ComlinkValueError(f"Relic tier must be between 1 and 9 inclusive.")


def positive_int(_, attribute, value):
    if value < 0:
        raise ComlinkValueError(f"{attribute.name} must be a positive integer.")


