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
        # Print less verbosely, maybe only on significant changes or if debugging
        # print(f"Added {amount} {mana_type.name} to pool. Current: {dict(self._pool)}")

    def can_spend(self, cost: 'ManaCost') -> bool:
        """Checks if the mana cost can be paid using available mana."""
        if not hasattr(cost, 'cost_dict'):
             print(f"Warning: can_spend called with incompatible cost type: {cost}")
             return False

        temp_pool = self._pool.copy() # Use a copy to simulate spending
        generic_cost = cost.cost_dict.get("generic", 0)

        # Check and simulate spending specific colored/colorless costs first
        for mana_type, amount in cost.cost_dict.items():
            if mana_type == "generic":
                continue # Handle generic cost later
            if temp_pool.get(mana_type, 0) < amount:
                return False # Not enough specific mana
            temp_pool[mana_type] -= amount
            if temp_pool[mana_type] == 0:
                del temp_pool[mana_type]

        # Check if remaining mana can cover the generic cost
        remaining_pool_total = sum(temp_pool.values())
        if remaining_pool_total < generic_cost:
            return False # Not enough total mana remaining for generic

        return True

    def spend(self, cost: 'ManaCost') -> bool:
        """Spends mana from the pool to pay the cost. Returns success/failure."""
        if not hasattr(cost, 'cost_dict'):
            print(f"Warning: spend called with incompatible cost type: {cost}")
            return False

        if not self.can_spend(cost): # Double check if payable
            print(f"Error: Attempted to spend unpayable cost {cost} from pool {self._pool}")
            return False

        print(f"Attempting to spend {cost} from pool {dict(self._pool)}")
        # --- Perform the actual spending --- 
        temp_pool = self._pool.copy()
        generic_to_pay = cost.cost_dict.get("generic", 0)
        colored_paid_for_generic = 0

        # 1. Pay specific colored/colorless costs
        for mana_type, amount in cost.cost_dict.items():
            if mana_type == "generic":
                continue
            # We already know we have enough due to can_spend check
            temp_pool[mana_type] -= amount
            if temp_pool[mana_type] == 0:
                del temp_pool[mana_type]

        # 2. Pay generic cost using remaining mana
        # Prioritize spending colorless, then colors (order might matter for complex cases)
        # Simple approach: Iterate through available mana types
        mana_types_for_generic = [ManaType.COLORLESS, ManaType.WHITE, ManaType.BLUE, ManaType.BLACK, ManaType.RED, ManaType.GREEN]
        for mana_type in mana_types_for_generic:
            available = temp_pool.get(mana_type, 0)
            spend_amount = min(generic_to_pay, available)
            if spend_amount > 0:
                temp_pool[mana_type] -= spend_amount
                generic_to_pay -= spend_amount
                if temp_pool[mana_type] == 0:
                    del temp_pool[mana_type]
            if generic_to_pay == 0:
                break
        
        # If generic_to_pay is still > 0 here, something went wrong (should be caught by can_spend)
        if generic_to_pay > 0:
             print(f"Error: Internal inconsistency during spending generic cost for {cost}. Remaining generic: {generic_to_pay}")
             # Don't update the pool, return failure
             return False

        # Commit the changes to the actual pool
        self._pool = temp_pool
        print(f"Spent {cost}. Pool after spend: {dict(self._pool)}")
        return True

    def get_amount(self, mana_type: 'ManaType') -> int:
        return self._pool.get(mana_type, 0)

    def empty(self) -> None:
        if self._pool:
            print(f"Emptying mana pool. Was: {dict(self._pool)}")
            self._pool.clear()

    def __repr__(self) -> str:
        return f"ManaPool({dict(self._pool)})" 