import random
from typing import NamedTuple
from darwin.creature import Creature


class Food(NamedTuple):
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

    def spawn_food(self, amount: int = 1, energy_value: float = 20.0) -> None:
        """Randomly spawns food within the environment bounds.

        Args:
            amount (int): Number of food items to spawn.
            energy_value (float): Energy provided by each food item.
        """
        for _ in range(amount):
            x = random.uniform(0, self.width)
            y = random.uniform(0, self.height)
            self.food_sources.append(Food(x, y, energy_value))

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

        Args:
            detection_radius (float): Distance within which a creature can eat food.

        Returns:
            int: Total number of food items consumed.
        """
        consumed_count = 0
        remaining_food = []

        for food in self.food_sources:
            eaten = False
            for creature in self.creatures:
                distance = (
                    (creature.x - food.x) ** 2 + (creature.y - food.y) ** 2
                ) ** 0.5
                if distance <= detection_radius:
                    creature.eat(food.energy)
                    eaten = True
                    consumed_count += 1
                    break

            if not eaten:
                remaining_food.append(food)

        self.food_sources = remaining_food
        return consumed_count

    def __repr__(self) -> str:
        return (
            f"Environment(size={self.width}x{self.height}, "
            f"creatures={len(self.creatures)}, "
            f"food={len(self.food_sources)})"
        )
