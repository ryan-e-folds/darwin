from unittest.mock import patch
from darwin.creature import Creature
from darwin.genome import Genome
import pytest


def test_creature_init() -> None:
    """Tests that Creature initializes correctly."""
    # This will be normalized to sum 3.0
    genome = Genome({"speed": 1.0, "size": 1.0, "strength": 1.0})
    creature = Creature(genome, energy=50.0, x=10.0, y=20.0, reproduce_sexually=True)

    assert creature.genome == genome
    assert creature.energy == 50.0
    assert creature.x == 10.0
    assert creature.y == 20.0
    assert creature.speed == pytest.approx(1.0)
    assert creature.strength == pytest.approx(1.0)
    assert creature.reproduce_sexually is True


def test_creature_move() -> None:
    """Tests that movement consumes energy and updates position."""
    # This will be normalized:
    # 0.2 + 0.1 + 0.0 (strength default added by Genome) = 0.3
    # Factor = 3.0 / 0.3 = 10.0
    # speed = 0.2 * 10.0 = 2.0
    # size = 0.1 * 10.0 = 1.0
    # strength = 0.0 * 10.0 = 0.0
    genome = Genome({"speed": 0.2, "size": 0.1})
    creature = Creature(genome, energy=100.0)

    creature.move(3.0, 4.0)  # distance = 5.0

    assert creature.x == 3.0
    assert creature.y == 4.0
    # cost = distance + size
    # cost = 5.0 + 1.0 = 6.0
    assert creature.energy == 94.0


def test_creature_reproduce_asexual() -> None:
    """Tests asexual reproduction (cloning)."""
    genome = Genome({"speed": 1.0, "size": 1.0, "strength": 1.0})
    creature = Creature(genome, energy=100.0, reproduce_sexually=False)

    child = creature.reproduce()

    assert child is not None
    assert creature.energy == 50.0
    assert child.energy == 50.0
    assert child.x == creature.x
    assert child.y == creature.y
    assert child.reproduce_sexually is False
    # Genome should be mutated, but derived from parent and normalized
    assert sum(child.genome.traits.values()) == pytest.approx(3.0)


def test_creature_reproduce_asexual_mismatch() -> None:
    """Tests that asexual creature returns None if other is provided."""
    creature = Creature(Genome(), reproduce_sexually=False)
    other = Creature(Genome())
    assert creature.reproduce(other) is None


def test_creature_reproduce_sexual() -> None:
    """Tests sexual reproduction (crossover)."""
    genome1 = Genome({"speed": 3.0, "size": 0.0, "strength": 0.0})
    genome2 = Genome({"speed": 0.0, "size": 3.0, "strength": 0.0})
    parent1 = Creature(genome1, energy=100.0, reproduce_sexually=True)
    parent2 = Creature(genome2, energy=100.0, reproduce_sexually=True)

    child = parent1.reproduce(parent2)

    assert child is not None
    assert parent1.energy == 50.0
    assert parent2.energy == 50.0
    # Child inherits 50 from parent1 and 50 from parent2
    assert child.energy == 100.0
    assert child.reproduce_sexually is True
    assert sum(child.genome.traits.values()) == pytest.approx(3.0)


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


def test_creature_fight_win() -> None:
    """Tests that a creature gains energy when winning a fight."""
    # attacker: strength=2.0, speed=0.0, size=1.0 (normalized)
    # defender: strength=0.0, speed=2.0, size=1.0 (normalized)
    attacker = Creature(
        Genome({"strength": 2.0, "speed": 0.0, "size": 1.0}), energy=100.0
    )
    defender = Creature(
        Genome({"strength": 0.0, "speed": 2.0, "size": 1.0}), energy=100.0
    )

    # win_prob = attacker.strength / (attacker.strength + defender.speed)
    # win_prob = 2.0 / (2.0 + 2.0) = 0.5
    # Force win by mocking random.random() to return 0.4
    with patch("random.random", return_value=0.4):
        won = attacker.fight(defender)

    assert won is True
    assert attacker.energy == 150.0
    assert defender.energy == 50.0


def test_creature_fight_loss() -> None:
    """Tests that a creature loses energy when losing a fight."""
    attacker = Creature(
        Genome({"strength": 2.0, "speed": 0.0, "size": 1.0}), energy=100.0
    )
    defender = Creature(
        Genome({"strength": 0.0, "speed": 2.0, "size": 1.0}), energy=100.0
    )

    # win_prob = 2.0 / (2.0 + 2.0) = 0.5
    # Force loss by mocking random.random() to return 0.6
    with patch("random.random", return_value=0.6):
        won = attacker.fight(defender)

    assert won is False
    assert attacker.energy == 50.0
    assert defender.energy == 150.0
