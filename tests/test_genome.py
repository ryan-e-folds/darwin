from darwin.genome import Genome


def test_genome_init() -> None:
    """Tests that Genome initializes correctly with traits."""
    traits = {"speed": 0.5, "size": 0.8}
    genome = Genome(traits)
    assert genome.traits == traits


def test_genome_mutate() -> None:
    """Tests that mutation modifies traits within expected bounds."""
    traits = {"speed": 0.5}
    genome = Genome(traits)
    # Use high mutation rate and strength to ensure change
    mutated = genome.mutate(mutation_rate=1.0, mutation_strength=0.1)

    assert "speed" in mutated.traits
    assert mutated.traits["speed"] != 0.5
    assert 0.4 <= mutated.traits["speed"] <= 0.6


def test_genome_crossover() -> None:
    """Tests that crossover produces a mix of traits from parents."""
    genome1 = Genome({"speed": 1.0, "size": 1.0})
    genome2 = Genome({"speed": 0.0, "size": 0.0})

    child = genome1.crossover(genome2)

    assert "speed" in child.traits
    assert "size" in child.traits
    assert child.traits["speed"] in [0.0, 1.0]
    assert child.traits["size"] in [0.0, 1.0]
