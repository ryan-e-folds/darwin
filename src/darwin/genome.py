import random
from typing import Self


class Genome:
    """Represents the genetic information of a Creature.

    Traits are stored as a dictionary of float values, typically normalized
    between 0.0 and 1.0.

    Attributes:
        traits (dict[str, float]): A dictionary mapping trait names to their values.
    """

    def __init__(self, traits: dict[str, float] | None = None) -> None:
        """Initializes the Genome with given traits or an empty dictionary.

        Args:
            traits (dict[str, float] | None): Initial traits for the genome.
        """
        self.traits = traits if traits is not None else {}

    def mutate(
        self, mutation_rate: float = 0.1, mutation_strength: float = 0.1
    ) -> Self:
        """Returns a new Genome with mutated traits.

        Each trait has a chance (mutation_rate) to be modified by a random value
        within [-mutation_strength, mutation_strength]. Values are clamped to [0.0, 1.0].

        Args:
            mutation_rate (float): Probability of each trait mutating (0.0 to 1.0).
            mutation_strength (float): Maximum amount a trait can change.

        Returns:
            Self: A new Genome instance with potentially mutated traits.
        """
        new_traits = {}
        for name, value in self.traits.items():
            if random.random() < mutation_rate:
                change = random.uniform(-mutation_strength, mutation_strength)
                new_value = max(0.0, min(1.0, value + change))
                new_traits[name] = new_value
            else:
                new_traits[name] = value
        return self.__class__(new_traits)

    def crossover(self, other: Self) -> Self:
        """Combines traits from this genome and another to create a child genome.

        For each trait, there is a 50% chance to inherit from either parent.

        Args:
            other (Self): The other Genome to crossover with.

        Returns:
            Self: A new Genome instance with a mix of traits from both parents.
        """
        new_traits = {}
        # Ensure we consider all traits present in either parent
        all_trait_names = set(self.traits.keys()) | set(other.traits.keys())

        for name in all_trait_names:
            parent = random.choice([self, other])
            if name in parent.traits:
                new_traits[name] = parent.traits[name]
            else:
                # If trait only exists in one parent and wasn't picked,
                # check the other parent.
                other_parent = other if parent is self else self
                new_traits[name] = other_parent.traits[name]

        return self.__class__(new_traits)

    def __repr__(self) -> str:
        return f"Genome(traits={self.traits})"
