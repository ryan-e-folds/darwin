from darwin.genome import Genome
import pytest


def test_genome_init() -> None:
    """Tests that Genome initializes correctly and normalizes core traits."""
    traits = {"speed": 0.5, "size": 0.5, "strength": 0.5}
    genome = Genome(traits)
    # They should already sum to 1.5, so they shouldn't change
    assert genome.traits["speed"] == pytest.approx(0.5)
    assert genome.traits["size"] == pytest.approx(0.5)
    assert genome.traits["strength"] == pytest.approx(0.5)

    # Test normalization
    traits2 = {"speed": 1.0, "size": 1.0, "strength": 1.0}
    genome2 = Genome(traits2)
    # Sum should be 1.5, so each should be 0.5
    assert sum(genome2.traits.values()) == pytest.approx(1.5)
    assert genome2.traits["speed"] == pytest.approx(0.5)


def test_genome_mutate() -> None:
    """Tests that mutation modifies traits and maintains normalization."""
    traits = {"speed": 0.5, "size": 0.5, "strength": 0.5}
    genome = Genome(traits)
    mutated = genome.mutate(mutation_rate=1.0, mutation_strength=0.2)

    assert sum(mutated.traits.values()) == pytest.approx(1.5)
    # At least one trait should have changed significantly
    assert any(mutated.traits[t] != 0.5 for t in ["speed", "size", "strength"])


def test_genome_crossover() -> None:
    """Tests that crossover produces a mix of traits and maintains normalization."""
    genome1 = Genome({"speed": 1.5, "size": 0.0, "strength": 0.0})
    genome2 = Genome({"speed": 0.0, "size": 1.5, "strength": 0.0})

    child = genome1.crossover(genome2)

    assert sum(child.traits.values()) == pytest.approx(1.5)
    for trait in ["speed", "size", "strength"]:
        assert trait in child.traits
