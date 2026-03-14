from unittest.mock import patch
from darwin.creature import Creature
from darwin.genome import Genome
import pytest


def test_creature_init() -> None:
    """Tests that Creature initializes correctly."""
    genome = Genome({"size": 0.8, "is_female": False, "attack": 0.7})
    creature = Creature(genome, energy=50.0, x=10.0, y=20.0)

    assert creature.genome == genome
    assert creature.energy == 50.0
    assert creature.age == 0
    assert creature.x == 10.0
    assert creature.y == 20.0
    assert creature.size == 0.8
    assert creature.attack == 0.7
    assert creature.defence == pytest.approx(0.3)
    assert creature.sex == "M"
    assert creature.id is not None
    assert isinstance(creature.id, str)


def test_creature_move() -> None:
    """Tests that movement consumes energy and updates position based on distance and size."""
    genome = Genome({"size": 0.5})
    creature = Creature(genome, energy=100.0)

    creature.move(3.0, 4.0)  # distance = 5.0

    assert creature.x == 3.0
    assert creature.y == 4.0
    assert creature.age == 1
    # cost = distance + size = 5.0 + 0.5 = 5.5
    assert creature.energy == 94.5


def test_creature_aging() -> None:
    """Tests that age increments and energy depletion increases after ADVANCED_AGE."""
    genome = Genome({"size": 0.5})
    creature = Creature(genome, energy=1000.0)

    # Set age to just before advanced age
    creature.age = creature.ADVANCED_AGE

    # Next move should still be normal cost (age will become ADVANCED_AGE + 1)
    # Wait, in my implementation:
    # self.age += 1
    # if self.age > self.ADVANCED_AGE: cost *= 2.0
    # So if age was ADVANCED_AGE, it becomes ADVANCED_AGE + 1, which IS > ADVANCED_AGE.

    creature.move(3.0, 4.0)  # distance = 5.0, cost = 5.5 * 2 = 11.0
    assert creature.age == creature.ADVANCED_AGE + 1
    assert creature.energy == 1000.0 - 11.0


def test_creature_reproduce_sexual() -> None:
    """Tests sexual reproduction (crossover)."""
    genome1 = Genome({"size": 1.0, "is_female": False})
    genome2 = Genome({"size": 0.0, "is_female": True})
    parent1 = Creature(genome1, energy=100.0)
    parent2 = Creature(genome2, energy=100.0)

    child = parent1.reproduce(parent2)

    assert child is not None
    assert parent1.energy == 50.0
    assert parent2.energy == 50.0
    assert child.energy == 100.0
    assert 0.0 <= child.size <= 1.0


def test_creature_reproduce_sexual_same_sex() -> None:
    """Tests that sexual reproduction fails between same-sex partners."""
    parent1 = Creature(Genome({"is_female": False}), energy=100.0)
    parent2 = Creature(Genome({"is_female": False}), energy=100.0)
    assert parent1.reproduce(parent2) is None


def test_creature_is_alive() -> None:
    """Tests life status based on energy."""
    creature = Creature(Genome(), energy=1.0)
    assert creature.is_alive is True

    creature.move(10.0, 10.0)  # distance approx 14.1, size 0.5
    assert creature.energy <= 0
    assert creature.is_alive is False


def test_creature_fight_win() -> None:
    """Tests that a creature gains fixed energy when winning a fight."""
    attacker = Creature(Genome({"attack": 1.0}), energy=100.0)
    defender = Creature(Genome({"attack": 0.5}), energy=100.0)

    # Force win
    with patch("random.random", return_value=0.0):
        won = attacker.fight(defender)

    assert won is True
    assert attacker.energy == 101.0
    assert defender.energy == 99.0


def test_creature_fight_loss() -> None:
    """Tests that a creature loses fixed energy when losing a fight."""
    attacker = Creature(Genome({"attack": 0.2}), energy=100.0)
    defender = Creature(Genome({"attack": 0.2}), energy=100.0)

    # Force loss
    with patch("random.random", return_value=0.9):
        won = attacker.fight(defender)

    assert won is False
    assert attacker.energy == 99.0
    assert defender.energy == 101.0


def test_creature_lineage() -> None:
    """Tests that creature unique IDs and lineage are correctly tracked."""
    parent1 = Creature(Genome({"is_female": False}), energy=100.0)
    parent2 = Creature(Genome({"is_female": True}), energy=100.0)

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
    parent1 = Creature(Genome({"is_female": False}), energy=200.0)
    parent2 = Creature(Genome({"is_female": True}), energy=200.0)
    child = parent1.reproduce(parent2)
    assert child is not None

    # Reset parent energy for next reproduction attempt
    parent1.energy = 200.0
    parent2.energy = 200.0
    child.energy = 200.0

    # Test reproduce with father
    assert child.reproduce(parent1) is None

    # Test reproduce with mother
    assert child.reproduce(parent2) is None

    # Test reproduce with offspring
    assert parent1.reproduce(child) is None


def test_creature_fight_relationship_check() -> None:
    """Tests that creatures cannot fight immediate relatives."""
    parent1 = Creature(Genome({"is_female": False}), energy=100.0)
    parent2 = Creature(Genome({"is_female": True}), energy=100.0)
    child = parent1.reproduce(parent2)
    assert child is not None

    # Force relationship check by ensuring they could fight otherwise
    assert child.fight(parent1) is False  # fight with father

    assert child.fight(parent2) is False  # fight with mother

    assert parent1.fight(child) is False  # fight with offspring
