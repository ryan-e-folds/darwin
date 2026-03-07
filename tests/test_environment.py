from darwin.environment import Environment, Food
from darwin.creature import Creature
from darwin.genome import Genome


def test_environment_init() -> None:
    """Tests that Environment initializes correctly."""
    env = Environment(width=200, height=150)
    assert env.width == 200
    assert env.height == 150
    assert len(env.creatures) == 0
    assert len(env.food_sources) == 0


def test_environment_spawn_food_fixed() -> None:
    """Tests that food spawns with fixed energy value when provided."""
    env = Environment(100, 100)
    env.spawn_food(amount=10, energy_value=15.0)

    assert len(env.food_sources) == 10
    for food in env.food_sources:
        assert 0 <= food.x <= 100
        assert 0 <= food.y <= 100
        assert food.energy == 15.0


def test_environment_spawn_food_random() -> None:
    """Tests that food spawns with random noise when energy_value is None."""
    env = Environment(100, 100)
    env.spawn_food(amount=100)  # Default is None

    assert len(env.food_sources) == 100
    energies = [food.energy for food in env.food_sources]
    
    # Check that all energies are within the noise range [15, 25]
    for energy in energies:
        assert 15.0 <= energy <= 25.0
    
    # Check that it's not all exactly 20.0 (very likely with 100 samples)
    assert any(e != 20.0 for e in energies)


def test_environment_handle_eating() -> None:
    """Tests that creatures eat food when close enough."""
    env = Environment(100, 100)
    creature = Creature(Genome(), x=50, y=50, energy=10)
    env.add_creature(creature)

    # Food right on top of creature
    env.food_sources.append(Food(50.0, 50.0, 20.0))
    # Food out of range
    env.food_sources.append(Food(10.0, 10.0, 20.0))

    consumed = env.handle_eating(detection_radius=2.0)

    assert consumed == 1
    assert len(env.food_sources) == 1
    assert creature.energy == 30.0


def test_environment_update_cleanup() -> None:
    """Tests that dead creatures are removed during update."""
    env = Environment()
    alive = Creature(Genome(), energy=10)
    dead = Creature(Genome(), energy=0)

    env.add_creature(alive)
    env.add_creature(dead)

    env.update()

    assert len(env.creatures) == 1
    assert env.creatures[0] is alive
