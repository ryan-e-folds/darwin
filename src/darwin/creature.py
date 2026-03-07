from typing import Self
from darwin.genome import Genome


class Creature:
    """An individual agent in the simulation.

    Attributes:
        genome (Genome): The genetic information of the creature.
        energy (float): Current energy levels. If it reaches 0, the creature dies.
        x (float): X-coordinate in the environment.
        y (float): Y-coordinate in the environment.
    """

    def __init__(
        self, genome: Genome, energy: float = 100.0, x: float = 0.0, y: float = 0.0
    ) -> None:
        """Initializes a Creature.

        Args:
            genome (Genome): Initial genome.
            energy (float): Starting energy.
            x (float): Initial x position.
            y (float): Initial y position.
        """
        self.genome = genome
        self.energy = energy
        self.x = x
        self.y = y

    @property
    def speed(self) -> float:
        """Returns the speed trait from the genome (default 0.1)."""
        return self.genome.traits.get("speed", 0.1)

    @property
    def size(self) -> float:
        """Returns the size trait from the genome (default 0.1)."""
        return self.genome.traits.get("size", 0.1)

    def move(self, dx: float, dy: float) -> None:
        """Moves the creature and consumes energy proportional to speed and distance.

        Args:
            dx (float): Change in x.
            dy (float): Change in y.
        """
        distance = (dx**2 + dy**2) ** 0.5
        # Energy cost: base cost + cost proportional to speed and distance
        cost = distance * (1.0 + self.speed * 5.0)
        self.energy -= cost
        self.x += dx
        self.y += dy

    def eat(self, amount: float) -> None:
        """Increases energy by eating.

        Args:
            amount (float): Amount of energy gained.
        """
        self.energy += amount

    def reproduce(self, other: Self | None = None) -> Self:
        """Creates a child creature.

        If 'other' is provided, performs sexual reproduction (crossover).
        Otherwise, performs asexual reproduction (cloning).
        The child's genome is always mutated.

        Args:
            other (Self | None): Optional partner for reproduction.

        Returns:
            Self: A new Creature instance.
        """
        if other:
            child_genome = self.genome.crossover(other.genome)
        else:
            child_genome = Genome(self.traits_copy())

        mutated_genome = child_genome.mutate()

        # Share energy with child
        child_energy = self.energy / 2
        self.energy /= 2

        return self.__class__(
            genome=mutated_genome, energy=child_energy, x=self.x, y=self.y
        )

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
            f"speed={self.speed:.2f})"
        )
