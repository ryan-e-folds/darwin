from darwin.evolution import Evolution


def test_evolution_init() -> None:
    """Tests that Evolution initializes correctly."""
    sim = Evolution(width=100, height=100)
    assert sim.generation == 0
    assert len(sim.environment.creatures) == 0


def test_evolution_seed_population() -> None:
    """Tests seeding the population."""
    sim = Evolution()
    sim.seed_population(count=10, initial_traits={"speed": 0.5})
    assert len(sim.environment.creatures) == 10
    for creature in sim.environment.creatures:
        assert creature.speed == 0.5


def test_evolution_step() -> None:
    """Tests that a simulation step updates state."""
    sim = Evolution()
    sim.seed_population(count=5, initial_traits={"speed": 0.5})
    initial_energy = sum(c.energy for c in sim.environment.creatures)

    sim.step()

    # Energy should have changed (likely decreased due to movement)
    new_energy = sum(c.energy for c in sim.environment.creatures)
    assert new_energy != initial_energy


def test_evolution_stats() -> None:
    """Tests that stats are calculated correctly."""
    sim = Evolution()
    sim.seed_population(count=2, initial_traits={"speed": 0.6})

    stats = sim.stats
    assert stats["population"] == 2
    assert stats["avg_speed"] == 0.6
    assert "avg_energy" in stats
