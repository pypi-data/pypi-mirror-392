"""
    This module provides some functional programming tools.
"""
from ._functional import (
    ensure_collection, first, create_id_index, nth_element, substitute_for_none, negate, identity,
    nonordered_groupby, map_all_values_of_the_dictionary, nonunique_id_index,
    IdIndex, IDT,
    Function, Provider, Consumer, Predicate
)

__all__ = [
    "first", "create_id_index", "nth_element", "substitute_for_none", "identity", "negate",
    "nonordered_groupby", "map_all_values_of_the_dictionary", "nonunique_id_index",
    "IdIndex", "IDT",
    "Function", "Provider", "Consumer", "Predicate"
]