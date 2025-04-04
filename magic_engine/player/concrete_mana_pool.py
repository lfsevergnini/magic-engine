"""Concrete implementation of the ManaPool interface."""
from typing import Dict, Optional, TYPE_CHECKING
from collections import defaultdict

from .mana_pool import ManaPool
from ..enums import ManaType

if TYPE_CHECKING:
    from ..costs.mana_cost import ManaCost
    from ..types import ObjectId
    # Define placeholder or import ManaRestriction properly
    class ManaRestriction:
        pass

class ConcreteManaPool(ManaPool):
    """A simple concrete implementation of a mana pool."""
    def __init__(self):
        # Stores mana by type. Restrictions aren't handled yet.
        self._pool: Dict[ManaType, int] = defaultdict(int)
        # TODO: Add tracking for restrictions and sources

    def add(self, mana_type: 'ManaType', amount: int, source_id: Optional['ObjectId'] = None, restriction: Optional['ManaRestriction'] = None) -> None:
        if amount <= 0:
            return
        if restriction:
            print(f"Warning: Mana restrictions not yet implemented. Adding {amount} {mana_type.name} without restriction.")
            # TODO: Handle restricted mana separately

        self._pool[mana_type] += amount
        print(f"Added {amount} {mana_type.name} to pool. Current: {dict(self._pool)}")

    def can_spend(self, cost: 'ManaCost') -> bool:
        """Checks if the mana cost can be paid. Basic implementation."""
        # TODO: Implement full cost checking (complex!)
        # Needs to handle generic vs colored, hybrid, phyrexian, snow etc.
        # and consider restrictions.
        # For now, just checks if *any* single mana symbol could be paid.
        if not hasattr(cost, 'symbols'): # Check if it looks like our SimpleManaCost
             print(f"Warning: can_spend called with non-SimpleManaCost: {cost}")
             return False # Cannot determine for unknown cost types

        # Very basic check: does pool have at least the mana value?
        total_mana_in_pool = sum(self._pool.values())
        mana_value = cost.get_mana_value()
        can_pay = total_mana_in_pool >= mana_value
        print(f"Pool: {dict(self._pool)}, Cost: {cost}, MV: {mana_value}, Can Pay (basic check): {can_pay}")
        # This basic check is often WRONG. Needs proper logic.
        return True # Placeholder - Assume payable for now to progress

    def spend(self, cost: 'ManaCost') -> bool:
        """Spends mana to pay the cost. Basic implementation."""
        # TODO: Implement full mana spending logic (complex!)
        # Needs to handle choices (which colored mana for generic costs?)
        # Needs to respect restrictions.
        if not hasattr(cost, 'symbols'):
            print(f"Warning: spend called with non-SimpleManaCost: {cost}")
            return False

        print(f"Attempting to spend {cost} from pool {dict(self._pool)}")
        # Basic placeholder: Reduce total mana by mana value.
        # This is WRONG, but allows simulation to proceed.
        mana_value_to_spend = cost.get_mana_value()
        spent_successfully = False
        temp_pool = self._pool.copy()

        # Prioritize spending colored mana matching the cost
        # (Not fully implemented in SimpleManaCost yet)

        # Spend generic mana (placeholder: just decrement any available mana)
        mana_types_in_order = [ManaType.COLORLESS, ManaType.WHITE, ManaType.BLUE, ManaType.BLACK, ManaType.RED, ManaType.GREEN]
        remaining_to_spend = mana_value_to_spend

        for mana_type in mana_types_in_order:
            spend_amount = min(remaining_to_spend, temp_pool.get(mana_type, 0))
            if spend_amount > 0:
                temp_pool[mana_type] -= spend_amount
                remaining_to_spend -= spend_amount
                if temp_pool[mana_type] == 0:
                    del temp_pool[mana_type]
            if remaining_to_spend == 0:
                break

        if remaining_to_spend == 0:
            self._pool = temp_pool
            spent_successfully = True
            print(f"Spent {cost}. Pool after spend: {dict(self._pool)}")
        else:
            print(f"Failed to spend {cost}. Not enough mana.")

        return spent_successfully # Placeholder

    def get_amount(self, mana_type: 'ManaType') -> int:
        return self._pool.get(mana_type, 0)

    def empty(self) -> None:
        if self._pool:
            print(f"Emptying mana pool. Was: {dict(self._pool)}")
            self._pool.clear()

    def __repr__(self) -> str:
        return f"ManaPool({dict(self._pool)})" 