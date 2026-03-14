import random
import uuid
from typing import Self, Literal
from darwin.genome import Genome


class Creature:
    """An individual agent in the simulation.

    Attributes:
        id (str): A unique identifier for the creature.
        genome (Genome): The genetic information of the creature.
        energy (float): Current energy levels. If it reaches 0, the creature dies.
        age (int): The current age of the creature (number of moves/steps).
        x (float): X-coordinate in the environment.
        y (float): Y-coordinate in the environment.
        mother_id (str | None): ID of the mother.
        father_id (str | None): ID of the father.
        offspring_ids (list[str]): List of unique IDs of offspring.
    """

    ADVANCED_AGE = 100

    def __init__(
        self,
        genome: Genome,
        energy: float = 100.0,
        x: float = 0.0,
        y: float = 0.0,
        mother_id: str | None = None,
        father_id: str | None = None,
    ) -> None:
        """Initializes a Creature.

        Args:
            genome (Genome): Initial genome.
            energy (float): Starting energy.
            x (float): Initial x position.
            y (float): Initial y position.
            mother_id (str | None): Unique ID of the mother.
            father_id (str | None): Unique ID of the father.
        """
        self.id = str(uuid.uuid4())
        self.genome = genome
        self.energy = energy
        self.age = 0
        self.x = x
        self.y = y
        self.mother_id = mother_id
        self.father_id = father_id
        self.offspring_ids: list[str] = []

    @property
    def sex(self) -> Literal["M", "F"]:
        """Returns the sex of the creature based on the genome's is_female trait."""
        return "F" if self.genome.traits.get("is_female", False) else "M"

    @property
    def size(self) -> float:
        """Returns the size trait from the genome (default 0.5)."""
        return float(self.genome.traits.get("size", 0.5))

    @property
    def attack(self) -> float:
        """Returns the attack trait from the genome (default 0.5)."""
        return float(self.genome.traits.get("attack", 0.5))

    @property
    def defence(self) -> float:
        """Returns the defence value, which is 1 - attack."""
        return 1.0 - self.attack

    def move(self, dx: float, dy: float) -> None:
        """Moves the creature and consumes energy proportional to distance and size.

        Increments age and increases energy cost if advanced age is reached.

        Args:
            dx (float): Change in x.
            dy (float): Change in y.
        """
        self.age += 1
        distance = (dx**2 + dy**2) ** 0.5
        # Energy cost: distance moved plus a cost proportional to size
        cost = distance + self.size

        # If advanced age is reached, energy depletes twice as fast
        if self.age > self.ADVANCED_AGE:
            cost *= 2.0

        self.energy -= cost
        self.x += dx
        self.y += dy

    def eat(self, amount: float) -> float:
        """Increases energy by eating.

        The amount of energy gained is capped by the creature's size.

        Args:
            amount (float): Amount of energy to potentially gain.

        Returns:
            float: The amount of energy actually consumed.
        """
        consumed = min(amount, 3 * self.size)
        self.energy += consumed
        return consumed

    def reproduce(self, other: Self) -> Self | None:
        """Creates a child creature through sexual reproduction.

        Opposite sex is required. The child's genome is a crossover
        of parents' genomes and is always mutated.
        Creatures cannot reproduce with parents or offspring.

        Args:
            other (Self): Partner for reproduction.

        Returns:
            Self | None: A new Creature instance, or None if mismatch occurs.
        """
        if self.sex == other.sex:
            return None

        # Relationship check
        if (
            other.id == self.mother_id
            or other.id == self.father_id
            or other.id in self.offspring_ids
        ):
            return None

        child_genome = self.genome.crossover(other.genome)
        # Share energy with child from both parents
        child_energy = (self.energy / 2) + (other.energy / 2)
        self.energy /= 2
        other.energy /= 2

        mutated_genome = child_genome.mutate()

        # Convention: mother is 'F', father is 'M'
        if self.sex == "F":
            mother_id, father_id = self.id, other.id
        else:
            mother_id, father_id = other.id, self.id

        child = self.__class__(
            genome=mutated_genome,
            energy=child_energy,
            x=self.x,
            y=self.y,
            mother_id=mother_id,
            father_id=father_id,
        )

        self.offspring_ids.append(child.id)
        other.offspring_ids.append(child.id)

        return child

    def fight(self, other: Self) -> bool:
        """Fights another creature.

        The chance of winning increases with self.attack and decreases with other.defence.
        If this creature wins, it gains 1.0 energy and the other loses 1.0.
        If it loses, it loses 1.0 energy and the other gains 1.0.
        Creatures cannot fight parents or offspring.

        Args:
            other (Self): The creature to fight.

        Returns:
            bool: True if this creature won the fight, False otherwise.
        """
        # Relationship check
        if (
            other.id == self.mother_id
            or other.id == self.father_id
            or other.id in self.offspring_ids
        ):
            return False

        # Chance of winning: attacker attack vs defender defence
        total_power = self.attack + other.defence
        if total_power == 0:
            win_probability = 0.0
        else:
            win_probability = self.attack / total_power

        if random.random() < win_probability:
            # Win! Gain 1.0 energy, defender loses 1.0
            self.energy += 1.0
            other.energy -= 1.0
            return True
        else:
            # Loss! Lose 1.0 energy, defender gains 1.0
            self.energy -= 1.0
            other.energy += 1.0
            return False

    def traits_copy(self) -> dict[str, float | bool]:
        """Returns a copy of the genome's traits."""
        return self.genome.traits.copy()

    @property
    def is_alive(self) -> bool:
        """Returns True if the creature has energy left."""
        return self.energy > 0

    def __repr__(self) -> str:
        return (
            f"Creature(id={self.id[:8]}, energy={self.energy:.1f}, "
            f"pos=({self.x:.1f}, {self.y:.1f}), "
            f"size={self.size:.2f}, "
            f"sex={self.sex})"
        )
