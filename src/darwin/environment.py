import random
from dataclasses import dataclass
from darwin.creature import Creature


@dataclass
class Food:
    """Represents a food source in the environment."""

    x: float
    y: float
    energy: float


class Environment:
    """Manages the simulation space, resources, and creatures.

    Attributes:
        width (float): Maximum x-coordinate.
        height (float): Maximum y-coordinate.
        creatures (list[Creature]): List of creatures currently in the environment.
        food_sources (list[Food]): List of available food sources.
    """

    def __init__(self, width: float = 100.0, height: float = 100.0) -> None:
        """Initializes the Environment.

        Args:
            width (float): Environment width.
            height (float): Environment height.
        """
        self.width = width
        self.height = height
        self.creatures: list[Creature] = []
        self.food_sources: list[Food] = []

    def add_creature(self, creature: Creature) -> None:
        """Adds a creature to the environment.

        Args:
            creature (Creature): The creature to add.
        """
        self.creatures.append(creature)

    def spawn_food(self, amount: int = 1, energy_value: float | None = None) -> None:
        """Randomly spawns food within the environment bounds.

        Args:
            amount (int): Number of food items to spawn.
            energy_value (float | None): Energy provided by each food item.
                If None, a base of 20.0 with random noise (+/- 5.0) is used.
        """
        for _ in range(amount):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)

            if energy_value is None:
                # Base energy with noise
                current_energy = 20.0 + random.uniform(-5, 5)
            else:
                current_energy = energy_value

            self.food_sources.append(Food(x, y, current_energy))

    def update(self) -> None:
        """Performs one simulation step.

        Removes dead creatures and handles interactions.
        """
        # Remove dead creatures
        self.creatures = [c for c in self.creatures if c.is_alive]

        # Interactions could be added here (e.g., eating, colliding)
        # For now, we'll keep it simple and just manage the populations.

    def handle_eating(self, detection_radius: float = 2.0) -> int:
        """Creatures eat food if they are within the detection radius.

        A creature eats an amount equal to its size (capped by food energy),
        which reduces the food's energy. Food is only removed when its
        energy reaches 0. Multiple creatures can eat from the same food
        source in one step.

        Args:
            detection_radius (float): Distance within which a creature can eat food.

        Returns:
            int: Total number of food items fully consumed (energy reaches 0).
        """
        consumed_count = 0
        remaining_food = []

        for food in self.food_sources:
            for creature in self.creatures:
                distance = (
                    (creature.x - food.x) ** 2 + (creature.y - food.y) ** 2
                ) ** 0.5
                if distance <= detection_radius:
                    # Amount eaten is the smallest of creature size or food energy
                    amount_to_eat = min(creature.size, food.energy)
                    creature.eat(amount_to_eat)
                    food.energy -= amount_to_eat

                if food.energy <= 1e-9:  # Effectively consumed
                    consumed_count += 1
                    break

            if food.energy > 1e-9:
                remaining_food.append(food)

        self.food_sources = remaining_food
        return consumed_count

    def __repr__(self) -> str:
        return (
            f"Environment(size={self.width}x{self.height}, "
            f"creatures={len(self.creatures)}, "
            f"food={len(self.food_sources)})"
        )
