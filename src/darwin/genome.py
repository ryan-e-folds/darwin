import random
from typing import Self


class Genome:
    """Represents the genetic information of a Creature.

    Traits are stored as a dictionary of float or boolean values.
    All float traits are constrained between 0.0 and 1.0.
    Traits are independent and no longer subject to normalization budgets.

    Attributes:
        traits (dict[str, float | bool]): A dictionary mapping trait names to their values.
    """

    # Traits that influence creature behaviors and attributes
    # is_female determines the sex of the creature.
    CORE_TRAITS = {"size", "is_female", "attack"}

    def __init__(self, traits: dict[str, float | bool] | None = None) -> None:
        """Initializes the Genome with given traits and ensures constraints.

        Args:
            traits (dict[str, float | bool] | None): Initial traits for the genome.
        """
        self.traits = traits if traits is not None else {}
        self._ensure_defaults()
        self._ensure_constraints()

    def _ensure_defaults(self) -> None:
        """Ensures that core traits exist with default values if not provided."""
        if "size" not in self.traits:
            # Default size to 0.5 if not specified
            self.traits["size"] = 0.5

        if "is_female" not in self.traits:
            # Default sex is assigned randomly if not specified
            self.traits["is_female"] = random.choice([True, False])

        if "attack" not in self.traits:
            # Default attack to 0.5 if not specified
            self.traits["attack"] = 0.5

    def _ensure_constraints(self) -> None:
        """Ensures all float traits are within [0, 1] and types are correct."""
        for name, value in self.traits.items():
            if isinstance(value, bool):
                continue
            if isinstance(value, (int, float)):
                self.traits[name] = max(0.0, min(1.0, float(value)))

    def mutate(
        self, mutation_rate: float = 0.1, mutation_strength: float = 0.1
    ) -> Self:
        """Returns a new Genome with mutated traits.

        Float traits have a chance (mutation_rate) to be modified by a random value
        within [-mutation_strength, mutation_strength]. Boolean traits are flipped.
        The new genome then ensures constraints are met.

        Args:
            mutation_rate (float): Probability of each trait mutating (0.0 to 1.0).
            mutation_strength (float): Maximum amount a float trait can change.

        Returns:
            Self: A new Genome instance with potentially mutated traits.
        """
        new_traits = self.traits.copy()
        for name, value in new_traits.items():
            if random.random() < mutation_rate:
                if isinstance(value, bool):
                    new_traits[name] = not value
                else:
                    change = random.uniform(-mutation_strength, mutation_strength)
                    new_traits[name] = float(value) + change

        return self.__class__(new_traits)

    def crossover(self, other: Self) -> Self:
        """Combines traits from this genome and another to create a child genome.

        Boolean traits are selected by random selection between the parents.
        Float traits are selected by random selection of a value between the
        parents' values.

        Args:
            other (Self): The other Genome to crossover with.

        Returns:
            Self: A new Genome instance with a mix of traits.
        """
        new_traits = {}
        all_trait_names = set(self.traits.keys()) | set(other.traits.keys())

        for name in all_trait_names:
            v1 = self.traits.get(name)
            v2 = other.traits.get(name)

            if v1 is not None and v2 is not None:
                if isinstance(v1, bool):
                    new_traits[name] = random.choice([v1, v2])
                else:
                    new_traits[name] = random.uniform(float(v1), float(v2))
            else:
                # Inherit the trait that only one parent has
                new_traits[name] = v1 if v1 is not None else v2

        return self.__class__(new_traits)

    def __repr__(self) -> str:
        return f"Genome(traits={ {k: round(v, 3) if isinstance(v, float) else v for k, v in self.traits.items()} })"
