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


def test_environment_handle_eating() -> None:
    """Tests that creatures eat food when close enough."""
    env = Environment(100, 100)
    # Default size 0.5
    creature = Creature(Genome(), x=50, y=50, energy=10)
    env.add_creature(creature)

    # Food right on top of creature
    env.food_sources.append(Food(50.0, 50.0, 20.0))
    # Food out of range
    env.food_sources.append(Food(10.0, 10.0, 20.0))

    consumed = env.handle_eating(detection_radius=2.0)

    # size 0.5, so min(0.5, 20.0) = 0.5 eaten. 19.5 remains.
    assert consumed == 0
    assert len(env.food_sources) == 2
    assert any(f.energy == 19.5 for f in env.food_sources)
    assert creature.energy == 10.5
