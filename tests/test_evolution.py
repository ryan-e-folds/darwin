from darwin.evolution import Evolution
import pytest


def test_evolution_init() -> None:
    """Tests that Evolution initializes correctly."""
    evo = Evolution(width=100, height=100)
    assert evo.steps == 0
    assert len(evo.environment.creatures) == 0
    assert evo.history == []


def test_evolution_seed_population() -> None:
    """Tests seeding the population."""
    evo = Evolution()
    # speed: 0.5, size: 0.0, strength: 0.0 -> normalized to 1.5, 0.0, 0.0
    evo.seed_population(count=10, initial_traits={"speed": 0.5})
    assert len(evo.environment.creatures) == 10
    for creature in evo.environment.creatures:
        assert creature.speed == pytest.approx(1.5)


def test_evolution_seed_population_random_sexuality() -> None:
    """Tests that reproduce_sexually is randomly assigned."""
    evo = Evolution()
    # Seed a large enough population to almost guarantee both True and False
    evo.seed_population(count=100, initial_traits={"speed": 0.5})
    
    sexual_count = sum(1 for c in evo.environment.creatures if c.reproduce_sexually)
    asexual_count = sum(1 for c in evo.environment.creatures if not c.reproduce_sexually)
    
    assert sexual_count > 0
    assert asexual_count > 0


def test_evolution_seed_population_energy_noise() -> None:
    """Tests that starting energy has random noise."""
    evo = Evolution()
    evo.seed_population(count=100, initial_traits={"speed": 0.5})
    
    energies = [c.energy for c in evo.environment.creatures]
    
    # Check that all energies are within [90, 110]
    for energy in energies:
        assert 90.0 <= energy <= 110.0
    
    # Check that not all are exactly 100.0
    assert any(e != 100.0 for e in energies)


def test_evolution_step() -> None:
    """Tests that a simulation step updates state."""
    evo = Evolution()
    evo.seed_population(count=5, initial_traits={"speed": 0.5, "size": 0.5, "strength": 0.5})
    initial_energy = sum(c.energy for c in evo.environment.creatures)

    evo.step()

    # Energy should have changed (likely decreased due to movement)
    new_energy = sum(c.energy for c in evo.environment.creatures)
    assert new_energy != initial_energy


def test_evolution_stats() -> None:
    """Tests that stats are calculated correctly."""
    evo = Evolution()
    # speed: 0.6, size: 0.4, strength: 0.5 -> sum 1.5, already normalized
    evo.seed_population(count=2, initial_traits={"speed": 0.6, "size": 0.4, "strength": 0.5})

    stats = evo.stats
    assert stats["population"] == 2
    assert stats["avg_speed"] == pytest.approx(0.6)
    assert stats["avg_size"] == pytest.approx(0.4)
    assert stats["avg_strength"] == pytest.approx(0.5)
    assert "avg_energy" in stats


def test_evolution_run_and_history() -> None:
    """Tests that run executes steps and records history."""
    evo = Evolution()
    evo.seed_population(count=5, initial_traits={"speed": 0.5})
    
    evo.run(steps=5, food_spawn_rate=2)
    
    assert evo.steps == 5
    assert len(evo.history) == 5
    for i, entry in enumerate(evo.history):
        assert entry["step"] == i + 1
        assert "population" in entry
