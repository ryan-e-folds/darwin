from darwin.environment import Environment
from darwin.creature import Creature
from darwin.genome import Genome
import random


class Evolution:
    """Orchestrates the evolution simulation.

    Attributes:
        environment (Environment): The simulation environment.
        steps (int): The number of steps executed.
        history (list[dict[str, float]]): Recorded stats after each step.
    """

    def __init__(self, width: float = 100.0, height: float = 100.0) -> None:
        """Initializes the Evolution simulation.

        Args:
            width (float): Environment width.
            height (float): Environment height.
        """
        self.environment = Environment(width, height)
        self.steps = 0
        self.history: list[dict[str, float]] = []

    def seed_population(self, count: int, initial_traits: dict[str, float]) -> None:
        """Creates an initial population of creatures with random positions and energy.

        Args:
            count (int): Number of creatures to spawn.
            initial_traits (dict[str, float]): Starting traits for all creatures.
        """
        for _ in range(count):
            genome = Genome(initial_traits.copy())
            x = random.uniform(0, self.environment.width)
            y = random.uniform(0, self.environment.height)
            reproduce_sexually = random.choice([True, False])
            # Base energy 100.0 with noise
            energy = 100.0 + random.uniform(-10, 10)
            creature = Creature(
                genome, 
                energy=energy, 
                x=x, 
                y=y, 
                reproduce_sexually=reproduce_sexually
            )
            self.environment.add_creature(creature)

    def step(self, food_spawn_rate: int = 0) -> None:
        """Executes a single time step in the simulation.

        Args:
            food_spawn_rate (int): Amount of food to spawn this step.
        """
        if food_spawn_rate > 0:
            self.environment.spawn_food(amount=food_spawn_rate)

        # 1. Movement
        self._move_creatures()

        # 2. Handle eating
        self.environment.handle_eating()

        # 3. Handle reproduction
        self._handle_reproduction()

        # 4. Cleanup dead and update environment
        self.environment.update()

        self.steps += 1
        self.history.append(self.stats)

    def _move_creatures(self) -> None:
        """Randomly moves all creatures in the environment."""
        for creature in self.environment.creatures:
            dx = random.uniform(-2, 2)
            dy = random.uniform(-2, 2)
            creature.move(dx, dy)

    def _handle_reproduction(
        self, energy_threshold: float = 150.0, partner_radius: float = 2.0
    ) -> None:
        """Handles both sexual and asexual reproduction for creatures.

        Args:
            energy_threshold (float): Minimum energy required to reproduce.
            partner_radius (float): Distance within which a sexual partner is sought.
        """
        new_borns = []
        already_reproduced = set()
        creatures = self.environment.creatures
        
        for i, creature in enumerate(creatures):
            if creature in already_reproduced:
                continue
                
            if creature.energy > energy_threshold:
                if creature.reproduce_sexually:
                    # Look for sexual partner nearby
                    partner = None
                    for j, potential_partner in enumerate(creatures):
                        if i == j or potential_partner in already_reproduced:
                            continue
                        if not potential_partner.reproduce_sexually or potential_partner.energy <= energy_threshold:
                            continue
                        
                        dist = ((creature.x - potential_partner.x)**2 + 
                                (creature.y - potential_partner.y)**2)**0.5
                        if dist < partner_radius:
                            partner = potential_partner
                            break
                    
                    if partner:
                        child = creature.reproduce(partner)
                        if child is not None:
                            new_borns.append(child)
                            already_reproduced.add(creature)
                            already_reproduced.add(partner)
                else:
                    # Asexual reproduction
                    child = creature.reproduce()
                    if child is not None:
                        new_borns.append(child)
                        already_reproduced.add(creature)

        for baby in new_borns:
            self.environment.add_creature(baby)

    def run(self, steps: int = 100, food_spawn_rate: int = 5) -> None:
        """Runs the simulation for a fixed number of steps.

        Args:
            steps (int): Number of steps to run.
            food_spawn_rate (int): Amount of food to spawn per step.
        """
        for _ in range(steps):
            self.step(food_spawn_rate=food_spawn_rate)

    @property
    def stats(self) -> dict[str, float]:
        """Returns summary statistics of the current population."""
        creatures = self.environment.creatures
        if not creatures:
            return {"step": self.steps, "population": 0}

        avg_speed = sum(c.speed for c in creatures) / len(creatures)
        avg_size = sum(c.size for c in creatures) / len(creatures)
        avg_strength = sum(c.strength for c in creatures) / len(creatures)
        avg_energy = sum(c.energy for c in creatures) / len(creatures)

        return {
            "step": self.steps,
            "population": float(len(creatures)),
            "avg_speed": avg_speed,
            "avg_size": avg_size,
            "avg_strength": avg_strength,
            "avg_energy": avg_energy,
        }
