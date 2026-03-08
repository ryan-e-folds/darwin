from darwin.evolution import Evolution
from darwin.creature import Creature
from darwin.genome import Genome
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
    # speed: 0.5, size: 0.0, strength: 0.0 -> normalized to 3.0, 0.0, 0.0
    evo.seed_population(count=10, initial_traits={"speed": 0.5})
    assert len(evo.environment.creatures) == 10
    for creature in evo.environment.creatures:
        assert creature.speed == pytest.approx(3.0)


def test_evolution_seed_population_random_sex() -> None:
    """Tests that sex is randomly assigned."""
    evo = Evolution()
    # Seed a large enough population to almost guarantee both M and F
    evo.seed_population(count=100, initial_traits={"speed": 0.5})

    m_count = sum(1 for c in evo.environment.creatures if c.sex == "M")
    f_count = sum(1 for c in evo.environment.creatures if c.sex == "F")

    assert m_count > 0
    assert f_count > 0


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
    evo.seed_population(
        count=5, initial_traits={"speed": 1.0, "size": 1.0, "strength": 1.0}
    )
    initial_energy = sum(c.energy for c in evo.environment.creatures)

    evo.step()

    # Energy should have changed (likely decreased due to movement)
    new_energy = sum(c.energy for c in evo.environment.creatures)
    assert new_energy != initial_energy


def test_evolution_stats() -> None:
    """Tests that stats are calculated correctly."""
    evo = Evolution()
    # speed: 0.6, size: 0.4, strength: 0.5 -> sum 1.5.
    # Factor = 3.0 / 1.5 = 2.0.
    # Normalized: 1.2, 0.8, 1.0.
    evo.seed_population(
        count=2, initial_traits={"speed": 0.6, "size": 0.4, "strength": 0.5}
    )

    stats = evo.stats
    assert stats["population"] == 2
    assert stats["avg_speed"] == pytest.approx(1.2)
    assert stats["avg_size"] == pytest.approx(0.8)
    assert stats["avg_strength"] == pytest.approx(1.0)
    assert "avg_energy" in stats


def test_evolution_seed_population_no_traits() -> None:
    """Tests seeding the population without providing initial traits."""
    evo = Evolution()
    evo.seed_population(count=5)
    assert len(evo.environment.creatures) == 5
    for creature in evo.environment.creatures:
        # Core traits should be initialized equally (3.0 / 3 = 1.0)
        assert creature.speed == pytest.approx(1.0)
        assert creature.size == pytest.approx(1.0)
        assert creature.strength == pytest.approx(1.0)


def test_evolution_run_and_history() -> None:
    """Tests that run executes steps and records history."""
    evo = Evolution()
    evo.seed_population(count=5, initial_traits={"speed": 1.0})

    evo.run(steps=5, food_spawn_rate=2)

    assert evo.steps == 5
    assert len(evo.history) == 5
    for i, entry in enumerate(evo.history):
        assert entry["step"] == i + 1
        assert "population" in entry


def test_evolution_handle_fighting() -> None:
    """Tests that _handle_fighting results in energy exchange between close creatures of same sex."""
    evo = Evolution(width=100, height=100)
    # Place two creatures of same sex very close to each other
    c1 = Creature(Genome(), energy=100.0, x=10.0, y=10.0, sex="M")
    c2 = Creature(Genome(), energy=100.0, x=10.5, y=10.5, sex="M")
    evo.environment.add_creature(c1)
    evo.environment.add_creature(c2)

    evo._handle_fighting(fight_radius=2.0)

    # One should have 150.0 and the other 50.0 (half energy exchange)
    energies = {c1.energy, c2.energy}
    assert energies == {150.0, 50.0}


def test_evolution_handle_fighting_opposite_sex() -> None:
    """Tests that _handle_fighting ignores close creatures of opposite sex."""
    evo = Evolution(width=100, height=100)
    # Place two creatures of opposite sex very close to each other
    c1 = Creature(Genome(), energy=100.0, x=10.0, y=10.0, sex="M")
    c2 = Creature(Genome(), energy=100.0, x=10.5, y=10.5, sex="F")
    evo.environment.add_creature(c1)
    evo.environment.add_creature(c2)

    evo._handle_fighting(fight_radius=2.0)

    # No energy exchange should have happened
    assert c1.energy == 100.0
    assert c2.energy == 100.0


def test_evolution_handle_reproduction_sexual_opposite_sex() -> None:
    """Tests that sexual reproduction occurs between opposite sex partners."""
    evo = Evolution(width=100, height=100)
    c1 = Creature(Genome(), energy=200.0, x=10.0, y=10.0, sex="M")
    c2 = Creature(Genome(), energy=200.0, x=10.5, y=10.5, sex="F")
    evo.environment.add_creature(c1)
    evo.environment.add_creature(c2)

    evo._handle_reproduction(energy_threshold=150.0, partner_radius=2.0)

    # Population should be 3 (parents + child)
    assert len(evo.environment.creatures) == 3


def test_evolution_handle_reproduction_sexual_same_sex() -> None:
    """Tests that sexual reproduction ignores same-sex partners."""
    evo = Evolution(width=100, height=100)
    c1 = Creature(Genome(), energy=200.0, x=10.0, y=10.0, sex="M")
    c2 = Creature(Genome(), energy=200.0, x=10.5, y=10.5, sex="M")
    evo.environment.add_creature(c1)
    evo.environment.add_creature(c2)

    evo._handle_reproduction(energy_threshold=150.0, partner_radius=2.0)

    # Population should still be 2
    assert len(evo.environment.creatures) == 2
