from darwin.creature import Creature
from darwin.genome import Genome
import pytest


def test_creature_init() -> None:
    """Tests that Creature initializes correctly."""
    # This will be normalized to sum 1.5
    genome = Genome({"speed": 0.5, "size": 0.5, "strength": 0.5})
    creature = Creature(genome, energy=50.0, x=10.0, y=20.0, reproduce_sexually=True)

    assert creature.genome == genome
    assert creature.energy == 50.0
    assert creature.x == 10.0
    assert creature.y == 20.0
    assert creature.speed == pytest.approx(0.5)
    assert creature.strength == pytest.approx(0.5)
    assert creature.reproduce_sexually is True


def test_creature_move() -> None:
    """Tests that movement consumes energy and updates position."""
    # This will be normalized:
    # 0.2 + 0.1 + 0.0 (strength default added by Genome) = 0.3
    # Factor = 1.5 / 0.3 = 5.0
    # speed = 0.2 * 5.0 = 1.0
    # size = 0.1 * 5.0 = 0.5
    # strength = 0.0 * 5.0 = 0.0
    genome = Genome({"speed": 0.2, "size": 0.1})
    creature = Creature(genome, energy=100.0)

    creature.move(3.0, 4.0)  # distance = 5.0

    assert creature.x == 3.0
    assert creature.y == 4.0
    # cost = distance * (1.0 + speed * 5.0 + size * 3.0)
    # cost = 5.0 * (1.0 + 1.0 * 5.0 + 0.5 * 3.0)
    # cost = 5.0 * (1.0 + 5.0 + 1.5) = 5.0 * 7.5 = 37.5
    assert creature.energy == 62.5


def test_creature_reproduce_asexual() -> None:
    """Tests asexual reproduction (cloning)."""
    genome = Genome({"speed": 0.5, "size": 0.5, "strength": 0.5})
    creature = Creature(genome, energy=100.0, reproduce_sexually=False)

    child = creature.reproduce()

    assert child is not None
    assert creature.energy == 50.0
    assert child.energy == 50.0
    assert child.x == creature.x
    assert child.y == creature.y
    assert child.reproduce_sexually is False
    # Genome should be mutated, but derived from parent and normalized
    assert sum(child.genome.traits.values()) == pytest.approx(1.5)


def test_creature_reproduce_asexual_mismatch() -> None:
    """Tests that asexual creature returns None if other is provided."""
    creature = Creature(Genome(), reproduce_sexually=False)
    other = Creature(Genome())
    assert creature.reproduce(other) is None


def test_creature_reproduce_sexual() -> None:
    """Tests sexual reproduction (crossover)."""
    genome1 = Genome({"speed": 1.5, "size": 0.0, "strength": 0.0})
    genome2 = Genome({"speed": 0.0, "size": 1.5, "strength": 0.0})
    parent1 = Creature(genome1, energy=100.0, reproduce_sexually=True)
    parent2 = Creature(genome2, energy=100.0, reproduce_sexually=True)

    child = parent1.reproduce(parent2)

    assert child is not None
    assert parent1.energy == 50.0
    assert child.energy == 50.0
    assert child.reproduce_sexually is True
    assert sum(child.genome.traits.values()) == pytest.approx(1.5)


def test_creature_reproduce_sexual_mismatch() -> None:
    """Tests that sexual creature returns None if no partner is provided."""
    creature = Creature(Genome(), reproduce_sexually=True)
    assert creature.reproduce() is None


def test_creature_reproduce_sexual_asexual_mismatch() -> None:
    """Tests that sexual creature returns None if partner is asexual."""
    parent1 = Creature(Genome(), reproduce_sexually=True)
    parent2 = Creature(Genome(), reproduce_sexually=False)
    assert parent1.reproduce(parent2) is None


def test_creature_is_alive() -> None:
    """Tests life status based on energy."""
    creature = Creature(Genome(), energy=1.0)
    assert creature.is_alive is True

    creature.move(10.0, 10.0)  # Should consume all energy
    assert creature.energy <= 0
    assert creature.is_alive is False
