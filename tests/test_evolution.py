from darwin.evolution import Evolution
import pytest


def test_evolution_init() -> None:
    """Tests that Evolution initializes correctly."""
    sim = Evolution(width=100, height=100)
    assert sim.generation == 0
    assert len(sim.environment.creatures) == 0


def test_evolution_seed_population() -> None:
    """Tests seeding the population."""
    sim = Evolution()
    # speed: 0.5, size: 0.0, strength: 0.0 -> normalized to 1.5, 0.0, 0.0
    sim.seed_population(count=10, initial_traits={"speed": 0.5})
    assert len(sim.environment.creatures) == 10
    for creature in sim.environment.creatures:
        assert creature.speed == pytest.approx(1.5)


def test_evolution_step() -> None:
    """Tests that a simulation step updates state."""
    sim = Evolution()
    sim.seed_population(count=5, initial_traits={"speed": 0.5, "size": 0.5, "strength": 0.5})
    initial_energy = sum(c.energy for c in sim.environment.creatures)

    sim.step()

    # Energy should have changed (likely decreased due to movement)
    new_energy = sum(c.energy for c in sim.environment.creatures)
    assert new_energy != initial_energy


def test_evolution_stats() -> None:
    """Tests that stats are calculated correctly."""
    sim = Evolution()
    # speed: 0.6, size: 0.4, strength: 0.5 -> sum 1.5, already normalized
    sim.seed_population(count=2, initial_traits={"speed": 0.6, "size": 0.4, "strength": 0.5})

    stats = sim.stats
    assert stats["population"] == 2
    assert stats["avg_speed"] == pytest.approx(0.6)
    assert stats["avg_size"] == pytest.approx(0.4)
    assert stats["avg_strength"] == pytest.approx(0.5)
    assert "avg_energy" in stats
