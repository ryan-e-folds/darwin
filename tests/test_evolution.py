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
    # size: 0.5, attack: 0.8
    evo.seed_population(count=10, initial_traits={"size": 0.5, "attack": 0.8})
    assert len(evo.environment.creatures) == 10
    for creature in evo.environment.creatures:
        assert creature.size == 0.5
        assert creature.attack == 0.8


def test_evolution_stats() -> None:
    """Tests that stats are calculated correctly."""
    evo = Evolution()
    evo.seed_population(count=2, initial_traits={"size": 0.4, "attack": 0.6})

    stats = evo.stats
    assert stats["population"] == 2
    assert stats["avg_size"] == pytest.approx(0.4)
    assert stats["avg_attack"] == pytest.approx(0.6)
    assert "avg_energy" in stats


def test_evolution_seed_population_no_traits() -> None:
    """Tests seeding the population without providing initial traits."""
    evo = Evolution()
    evo.seed_population(count=5)
    assert len(evo.environment.creatures) == 5
    for creature in evo.environment.creatures:
        # Defaults: size=0.5, attack=0.5
        assert creature.size == 0.5
        assert creature.attack == 0.5


def test_evolution_handle_fighting() -> None:
    """Tests that _handle_fighting results in energy exchange between close creatures of same sex."""
    evo = Evolution(width=100, height=100)
    # Place two creatures of same sex very close to each other
    # genome defaults to is_female=False (randomly, but let's be explicit)
    g1 = Genome({"is_female": False})
    g2 = Genome({"is_female": False})
    c1 = Creature(g1, energy=100.0, x=10.0, y=10.0)
    c2 = Creature(g2, energy=100.0, x=10.5, y=10.5)
    evo.environment.add_creature(c1)
    evo.environment.add_creature(c2)

    evo._handle_fighting(fight_radius=2.0)

    # One should have 101.0 and the other 99.0
    energies = {c1.energy, c2.energy}
    assert energies == {101.0, 99.0}


def test_evolution_handle_reproduction_sexual_opposite_sex() -> None:
    """Tests that sexual reproduction occurs between opposite sex partners above threshold."""
    evo = Evolution(width=100, height=100)
    # default energy_threshold is now 100.0
    c1 = Creature(Genome({"is_female": False}), energy=110.0, x=10.0, y=10.0)
    c2 = Creature(Genome({"is_female": True}), energy=110.0, x=10.5, y=10.5)
    evo.environment.add_creature(c1)
    evo.environment.add_creature(c2)

    evo._handle_reproduction(energy_threshold=100.0, partner_radius=2.0)

    # Population should be 3 (parents + child)
    assert len(evo.environment.creatures) == 3


def test_evolution_handle_reproduction_below_threshold() -> None:
    """Tests that sexual reproduction fails if parents are below energy threshold."""
    evo = Evolution(width=100, height=100)
    # default energy_threshold is 100.0
    c1 = Creature(Genome({"is_female": False}), energy=90.0, x=10.0, y=10.0)
    c2 = Creature(Genome({"is_female": True}), energy=90.0, x=10.5, y=10.5)
    evo.environment.add_creature(c1)
    evo.environment.add_creature(c2)

    evo._handle_reproduction(energy_threshold=100.0, partner_radius=2.0)

    # Population should still be 2
    assert len(evo.environment.creatures) == 2
