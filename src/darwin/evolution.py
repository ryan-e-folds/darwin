from darwin.environment import Environment
from darwin.creature import Creature
from darwin.genome import Genome
import random


class Evolution:
    """Orchestrates the evolution simulation.

    Attributes:
        environment (Environment): The simulation environment.
        generation (int): The current generation number.
    """

    def __init__(self, width: float = 100.0, height: float = 100.0) -> None:
        """Initializes the Evolution simulation.

        Args:
            width (float): Environment width.
            height (float): Environment height.
        """
        self.environment = Environment(width, height)
        self.generation = 0

    def seed_population(self, count: int, initial_traits: dict[str, float]) -> None:
        """Creates an initial population of creatures with random positions.

        Args:
            count (int): Number of creatures to spawn.
            initial_traits (dict[str, float]): Starting traits for all creatures.
        """
        for _ in range(count):
            genome = Genome(initial_traits.copy())
            x = random.uniform(0, self.environment.width)
            y = random.uniform(0, self.environment.height)
            creature = Creature(genome, x=x, y=y)
            self.environment.add_creature(creature)

    def step(self) -> None:
        """Executes a single time step in the simulation."""
        # 1. Random movement for all creatures
        for creature in self.environment.creatures:
            dx = random.uniform(-2, 2)
            dy = random.uniform(-2, 2)
            creature.move(dx, dy)

        # 2. Handle eating
        self.environment.handle_eating()

        # 3. Handle reproduction (simple logic: if energy > 150)
        new_borns = []
        for creature in self.environment.creatures:
            if creature.energy > 150:
                child = creature.reproduce()
                if child is not None:
                    new_borns.append(child)

        for baby in new_borns:
            self.environment.add_creature(baby)

        # 4. Cleanup dead and update environment
        self.environment.update()

    def run_generation(self, steps: int = 100, food_spawn_rate: int = 5) -> None:
        """Runs the simulation for a fixed number of steps.

        Args:
            steps (int): Number of steps to run.
            food_spawn_rate (int): Amount of food to spawn per step.
        """
        for _ in range(steps):
            self.environment.spawn_food(amount=food_spawn_rate)
            self.step()
        self.generation += 1

    @property
    def stats(self) -> dict[str, float]:
        """Returns summary statistics of the current population."""
        creatures = self.environment.creatures
        if not creatures:
            return {"population": 0}

        avg_speed = sum(c.speed for c in creatures) / len(creatures)
        avg_size = sum(c.size for c in creatures) / len(creatures)
        avg_strength = sum(c.strength for c in creatures) / len(creatures)
        avg_energy = sum(c.energy for c in creatures) / len(creatures)

        return {
            "generation": self.generation,
            "population": len(creatures),
            "avg_speed": avg_speed,
            "avg_size": avg_size,
            "avg_strength": avg_strength,
            "avg_energy": avg_energy,
        }
