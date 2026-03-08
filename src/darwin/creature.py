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
        x (float): X-coordinate in the environment.
        y (float): Y-coordinate in the environment.
        sex (Literal["M", "F"]): The sex of the creature.
        mother_id (str | None): ID of the mother.
        father_id (str | None): ID of the father.
        offspring_ids (list[str]): List of unique IDs of offspring.
    """

    def __init__(
        self,
        genome: Genome,
        energy: float = 100.0,
        x: float = 0.0,
        y: float = 0.0,
        sex: Literal["M", "F"] | None = None,
        mother_id: str | None = None,
        father_id: str | None = None,
    ) -> None:
        """Initializes a Creature.

        Args:
            genome (Genome): Initial genome.
            energy (float): Starting energy.
            x (float): Initial x position.
            y (float): Initial y position.
            sex (Literal["M", "F"] | None): The sex of the creature. If None, it is randomly assigned.
            mother_id (str | None): Unique ID of the mother.
            father_id (str | None): Unique ID of the father.
        """
        self.id = str(uuid.uuid4())
        self.genome = genome
        self.energy = energy
        self.x = x
        self.y = y
        self.sex = sex if sex is not None else random.choice(["M", "F"])
        self.mother_id = mother_id
        self.father_id = father_id
        self.offspring_ids: list[str] = []

    @property
    def speed(self) -> float:
        """Returns the speed trait from the genome (default 0.1)."""
        return self.genome.traits.get("speed", 0.1)

    @property
    def size(self) -> float:
        """Returns the size trait from the genome (default 0.1)."""
        return self.genome.traits.get("size", 0.1)

    @property
    def strength(self) -> float:
        """Returns the strength trait from the genome (default 0.1)."""
        return self.genome.traits.get("strength", 0.1)

    def move(self, dx: float, dy: float) -> None:
        """Moves the creature and consumes energy proportional to size, strength, speed and distance.

        Args:
            dx (float): Change in x.
            dy (float): Change in y.
        """
        distance = (dx**2 + dy**2) ** 0.5
        # Energy cost: distance moved plus a cost proportional to size and strength, reduced by speed
        cost = max(0.0, distance + self.size + self.strength - self.speed)
        self.energy -= cost
        self.x += dx
        self.y += dy

    def eat(self, amount: float) -> None:
        """Increases energy by eating.

        Args:
            amount (float): Amount of energy gained.
        """
        self.energy += amount

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

        The chance of winning increases with self.strength and self.size,
        and decreases with other.speed and other.size.
        If this creature wins, it takes half of the other's energy.
        If it loses, it loses half of its own energy (which goes to the other).
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

        # Chance of winning: attacker strength + size vs defender speed + size
        win_probability = (self.strength + self.size) / (
            self.strength + self.size + other.speed + other.size
        )

        if random.random() < win_probability:
            # Win! Take half of defender's energy
            energy_gain = other.energy / 2
            self.energy += energy_gain
            other.energy -= energy_gain
            return True
        else:
            # Loss! Lose half of own energy to defender
            energy_loss = self.energy / 2
            other.energy += energy_loss
            self.energy -= energy_loss
            return False

    def traits_copy(self) -> dict[str, float]:
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
            f"speed={self.speed:.2f}, "
            f"sex={self.sex})"
        )
