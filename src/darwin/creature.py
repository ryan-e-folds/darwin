import random
from typing import Self
from darwin.genome import Genome


class Creature:
    """An individual agent in the simulation.

    Attributes:
        genome (Genome): The genetic information of the creature.
        energy (float): Current energy levels. If it reaches 0, the creature dies.
        x (float): X-coordinate in the environment.
        y (float): Y-coordinate in the environment.
        reproduce_sexually (bool): Whether the creature reproduces sexually.
    """

    def __init__(
        self,
        genome: Genome,
        energy: float = 100.0,
        x: float = 0.0,
        y: float = 0.0,
        reproduce_sexually: bool = False,
    ) -> None:
        """Initializes a Creature.

        Args:
            genome (Genome): Initial genome.
            energy (float): Starting energy.
            x (float): Initial x position.
            y (float): Initial y position.
            reproduce_sexually (bool): True if sexual reproduction is required.
        """
        self.genome = genome
        self.energy = energy
        self.x = x
        self.y = y
        self.reproduce_sexually = reproduce_sexually

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
        """Moves the creature and consumes energy proportional to size and distance.

        Args:
            dx (float): Change in x.
            dy (float): Change in y.
        """
        distance = (dx**2 + dy**2) ** 0.5
        # Energy cost: distance moved plus a cost proportional to size
        cost = distance + self.size
        self.energy -= cost
        self.x += dx
        self.y += dy

    def eat(self, amount: float) -> None:
        """Increases energy by eating.

        Args:
            amount (float): Amount of energy gained.
        """
        self.energy += amount

    def reproduce(self, other: Self | None = None) -> Self | None:
        """Creates a child creature.

        If 'other' is provided, performs sexual reproduction (crossover).
        Otherwise, performs asexual reproduction (cloning).
        The child's genome is always mutated.

        Args:
            other (Self | None): Optional partner for reproduction.

        Returns:
            Self | None: A new Creature instance, or None if the mode mismatch occurs.
        """
        if self.reproduce_sexually:
            if other is None or not other.reproduce_sexually:
                return None
            child_genome = self.genome.crossover(other.genome)
            # Share energy with child from both parents
            child_energy = (self.energy / 2) + (other.energy / 2)
            self.energy /= 2
            other.energy /= 2
        else:
            if other is not None:
                return None
            child_genome = Genome(self.traits_copy())
            # Share energy with child
            child_energy = self.energy / 2
            self.energy /= 2

        mutated_genome = child_genome.mutate()

        return self.__class__(
            genome=mutated_genome,
            energy=child_energy,
            x=self.x,
            y=self.y,
            reproduce_sexually=self.reproduce_sexually,
        )

    def fight(self, other: Self) -> bool:
        """Fights another creature.

        The chance of winning increases with self.strength and decreases with other.speed.
        If this creature wins, it takes half of the other's energy.
        If it loses, it loses half of its own energy (which goes to the other).

        Args:
            other (Self): The creature to fight.

        Returns:
            bool: True if this creature won the fight, False otherwise.
        """
        # Chance of winning: attacker strength vs defender speed
        win_probability = self.strength / (self.strength + other.speed)

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
            f"Creature(energy={self.energy:.1f}, "
            f"pos=({self.x:.1f}, {self.y:.1f}), "
            f"speed={self.speed:.2f}, "
            f"sexual={self.reproduce_sexually})"
        )
