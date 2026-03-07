from darwin.creature import Creature
from darwin.genome import Genome


def test_creature_init() -> None:
    """Tests that Creature initializes correctly."""
    genome = Genome({"speed": 0.5})
    creature = Creature(genome, energy=50.0, x=10.0, y=20.0)

    assert creature.genome == genome
    assert creature.energy == 50.0
    assert creature.x == 10.0
    assert creature.y == 20.0
    assert creature.speed == 0.5


def test_creature_move() -> None:
    """Tests that movement consumes energy and updates position."""
    genome = Genome({"speed": 0.2})
    creature = Creature(genome, energy=100.0)

    creature.move(3.0, 4.0)  # distance = 5.0

    assert creature.x == 3.0
    assert creature.y == 4.0
    # cost = 5.0 * (1.0 + 0.2 * 5.0) = 5.0 * 2.0 = 10.0
    assert creature.energy == 90.0


def test_creature_reproduce_asexual() -> None:
    """Tests asexual reproduction (cloning)."""
    genome = Genome({"speed": 0.5})
    creature = Creature(genome, energy=100.0)

    child = creature.reproduce()

    assert creature.energy == 50.0
    assert child.energy == 50.0
    assert child.x == creature.x
    assert child.y == creature.y
    # Genome should be mutated, but derived from parent
    assert "speed" in child.genome.traits


def test_creature_is_alive() -> None:
    """Tests life status based on energy."""
    creature = Creature(Genome(), energy=1.0)
    assert creature.is_alive is True

    creature.move(10.0, 10.0)  # Should consume all energy
    assert creature.energy <= 0
    assert creature.is_alive is False
