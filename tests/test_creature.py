from unittest.mock import patch
from darwin.creature import Creature
from darwin.genome import Genome
import pytest


def test_creature_init() -> None:
    """Tests that Creature initializes correctly."""
    # This will be normalized to sum 3.0
    genome = Genome({"speed": 1.0, "size": 1.0, "strength": 1.0})
    creature = Creature(genome, energy=50.0, x=10.0, y=20.0, sex="M")

    assert creature.genome == genome
    assert creature.energy == 50.0
    assert creature.x == 10.0
    assert creature.y == 20.0
    assert creature.speed == pytest.approx(1.0)
    assert creature.strength == pytest.approx(1.0)
    assert creature.sex == "M"
    assert creature.id is not None
    assert isinstance(creature.id, str)


def test_creature_move() -> None:
    """Tests that movement consumes energy and updates position."""
    # This will be normalized:
    # 0.1 + 0.1 + 0.1 = 0.3
    # Factor = 3.0 / 0.3 = 10.0
    # speed = 0.1 * 10.0 = 1.0
    # size = 0.1 * 10.0 = 1.0
    # strength = 0.1 * 10.0 = 1.0
    genome = Genome({"speed": 0.1, "size": 0.1, "strength": 0.1})
    creature = Creature(genome, energy=100.0)

    creature.move(3.0, 4.0)  # distance = 5.0

    assert creature.x == 3.0
    assert creature.y == 4.0
    # cost = max(0.0, distance + size + strength - speed)
    # cost = max(0.0, 5.0 + 1.0 + 1.0 - 1.0) = 6.0
    assert creature.energy == 94.0


def test_creature_move_high_speed() -> None:
    """Tests that movement cost does not go below zero with high speed."""
    # speed=3.0, size=0.0, strength=0.0
    genome = Genome({"speed": 3.0, "size": 0.0, "strength": 0.0})
    creature = Creature(genome, energy=100.0)

    creature.move(1.0, 0.0)  # distance = 1.0

    # cost = max(0.0, 1.0 + 0.0 + 0.0 - 3.0) = 0.0
    assert creature.energy == 100.0


def test_creature_reproduce_sexual() -> None:
    """Tests sexual reproduction (crossover)."""
    genome1 = Genome({"speed": 3.0, "size": 0.0, "strength": 0.0})
    genome2 = Genome({"speed": 0.0, "size": 3.0, "strength": 0.0})
    parent1 = Creature(genome1, energy=100.0, sex="M")
    parent2 = Creature(genome2, energy=100.0, sex="F")

    child = parent1.reproduce(parent2)

    assert child is not None
    assert parent1.energy == 50.0
    assert parent2.energy == 50.0
    # Child inherits 50 from parent1 and 50 from parent2
    assert child.energy == 100.0
    assert sum(child.genome.traits.values()) == pytest.approx(3.0)


def test_creature_reproduce_sexual_same_sex() -> None:
    """Tests that sexual reproduction fails between same-sex partners."""
    parent1 = Creature(Genome(), energy=100.0, sex="M")
    parent2 = Creature(Genome(), energy=100.0, sex="M")
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

    # win_prob = (2.0 + 1.0) / (2.0 + 1.0 + 2.0 + 1.0) = 0.5
    # Force loss by mocking random.random() to return 0.6
    with patch("random.random", return_value=0.6):
        won = attacker.fight(defender)

    assert won is False
    assert attacker.energy == 50.0
    assert defender.energy == 150.0


def test_creature_fight_size_advantage() -> None:
    """Tests that size positively affects the chance of winning."""
    # Attacker: strength=1.0, size=2.0, speed=0.0 (Sum=3.0)
    # Defender: strength=1.0, size=1.0, speed=1.0 (Sum=3.0)
    attacker = Creature(
        Genome({"strength": 1.0, "size": 2.0, "speed": 0.0}), energy=100.0
    )
    defender = Creature(
        Genome({"strength": 1.0, "size": 1.0, "speed": 1.0}), energy=100.0
    )

    # win_prob = (attacker.strength + attacker.size) / (attacker.strength + attacker.size + defender.speed + defender.size)
    # win_prob = (1.0 + 2.0) / (1.0 + 2.0 + 1.0 + 1.0) = 3.0 / 5.0 = 0.6

    # Mock random.random() to return 0.55 (less than 0.6, so it's a win)
    with patch("random.random", return_value=0.55):
        won = attacker.fight(defender)

    assert won is True
    assert attacker.energy == 150.0


def test_creature_lineage() -> None:
    """Tests that creature unique IDs and lineage are correctly tracked."""
    parent1 = Creature(Genome(), energy=100.0, sex="M")
    parent2 = Creature(Genome(), energy=100.0, sex="F")

    child = parent1.reproduce(parent2)

    assert child is not None
    assert child.father_id == parent1.id
    assert child.mother_id == parent2.id
    assert child.id in parent1.offspring_ids
    assert child.id in parent2.offspring_ids
    assert len(parent1.offspring_ids) == 1
    assert len(parent2.offspring_ids) == 1


def test_creature_reproduce_relationship_check() -> None:
    """Tests that creatures cannot reproduce with immediate relatives."""
    parent1 = Creature(Genome(), energy=200.0, sex="M")
    parent2 = Creature(Genome(), energy=200.0, sex="F")
    child = parent1.reproduce(parent2)
    assert child is not None

    # Reset parent energy for next reproduction attempt
    parent1.energy = 200.0
    parent2.energy = 200.0
    child.energy = 200.0

    # Ensure child has opposite sex to parents for testing
    child.sex = "F"
    assert child.reproduce(parent1) is None  # reproduce with father

    child.sex = "M"
    assert child.reproduce(parent2) is None  # reproduce with mother

    parent1.sex = "M"
    assert parent1.reproduce(child) is None  # reproduce with offspring


def test_creature_fight_relationship_check() -> None:
    """Tests that creatures cannot fight immediate relatives."""
    parent1 = Creature(Genome(), energy=100.0, sex="M")
    parent2 = Creature(Genome(), energy=100.0, sex="F")
    child = parent1.reproduce(parent2)
    assert child is not None

    # Set same sex for fighting
    child.sex = "M"
    assert child.fight(parent1) is False  # fight with father

    parent2.sex = "M"
    assert child.fight(parent2) is False  # fight with mother

    assert parent1.fight(child) is False  # fight with offspring
