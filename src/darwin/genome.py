import random
from typing import Self


class Genome:
    """Represents the genetic information of a Creature.

    Traits are stored as a dictionary of float values. Certain traits
    (speed, size, strength) are normalized to reflect an evolutionary trade-off.

    Attributes:
        traits (dict[str, float]): A dictionary mapping trait names to their values.
    """

    # Traits that are subject to normalization trade-offs
    CORE_TRAITS = {"speed", "size", "strength"}
    TRAIT_BUDGET = 1.5

    def __init__(self, traits: dict[str, float] | None = None) -> None:
        """Initializes the Genome with given traits and normalizes them.

        Args:
            traits (dict[str, float] | None): Initial traits for the genome.
        """
        self.traits = traits if traits is not None else {}
        self._normalize_traits()

    def _normalize_traits(self) -> None:
        """Normalizes core traits so they sum to the TRAIT_BUDGET.

        This enforces trade-offs: if one trait is high, others must be lower.
        If no core traits are present, they are initialized to equal values.
        """
        present_core_traits = [t for t in self.CORE_TRAITS if t in self.traits]

        if not present_core_traits:
            # If no core traits, initialize them equally
            share = self.TRAIT_BUDGET / len(self.CORE_TRAITS)
            for trait in self.CORE_TRAITS:
                self.traits[trait] = share
            return

        # Sum current values of present core traits
        current_sum = sum(self.traits[t] for t in present_core_traits)

        if current_sum == 0:
            # Avoid division by zero, distribute budget equally among present traits
            share = self.TRAIT_BUDGET / len(present_core_traits)
            for trait in present_core_traits:
                self.traits[trait] = share
        else:
            # Scale present traits to meet the budget
            factor = self.TRAIT_BUDGET / current_sum
            for trait in present_core_traits:
                self.traits[trait] *= factor

        # Ensure all core traits exist (fill in missing ones with 0 or redistribute)
        # For simplicity, if some core traits are missing but others exist,
        # we only normalize those that are present.
        # But for a strict trade-off, we might want to ensure all CORE_TRAITS are present.
        for trait in self.CORE_TRAITS:
            if trait not in self.traits:
                self.traits[trait] = 0.0  # Or some small default

        # Re-normalize if we added zeros to ensure the sum is exactly TRAIT_BUDGET
        current_sum = sum(self.traits[t] for t in self.CORE_TRAITS)
        if current_sum > 0:
            factor = self.TRAIT_BUDGET / current_sum
            for trait in self.CORE_TRAITS:
                self.traits[trait] *= factor

    def mutate(
        self, mutation_rate: float = 0.1, mutation_strength: float = 0.1
    ) -> Self:
        """Returns a new Genome with mutated traits.

        Each trait has a chance (mutation_rate) to be modified by a random value
        within [-mutation_strength, mutation_strength]. The new genome is then re-normalized.

        Args:
            mutation_rate (float): Probability of each trait mutating (0.0 to 1.0).
            mutation_strength (float): Maximum amount a trait can change.

        Returns:
            Self: A new Genome instance with potentially mutated and normalized traits.
        """
        new_traits = self.traits.copy()
        for name, value in new_traits.items():
            if random.random() < mutation_rate:
                change = random.uniform(-mutation_strength, mutation_strength)
                # We allow it to go negative temporarily before normalization if needed,
                # but max(0, ...) is safer for traits.
                new_traits[name] = max(0.01, value + change)  # 0.01 to keep it alive

        return self.__class__(new_traits)

    def crossover(self, other: Self) -> Self:
        """Combines traits from this genome and another to create a child genome.

        For each trait, there is a 50% chance to inherit from either parent.
        The resulting traits are then normalized.

        Args:
            other (Self): The other Genome to crossover with.

        Returns:
            Self: A new Genome instance with a mix of normalized traits.
        """
        new_traits = {}
        all_trait_names = set(self.traits.keys()) | set(other.traits.keys())

        for name in all_trait_names:
            parent = random.choice([self, other])
            if name in parent.traits:
                new_traits[name] = parent.traits[name]
            else:
                other_parent = other if parent is self else self
                new_traits[name] = other_parent.traits[name]

        return self.__class__(new_traits)

    def __repr__(self) -> str:
        return f"Genome(traits={ {k: round(v, 3) for k, v in self.traits.items()} })"
