from darwin.genome import Genome


def test_genome_init() -> None:
    """Tests that Genome initializes correctly and handles CORE_TRAITS."""
    genome = Genome()
    # size should default to 0.5, is_female should be bool, attack should default to 0.5
    assert genome.traits["size"] == 0.5
    assert isinstance(genome.traits["is_female"], bool)
    assert genome.traits["attack"] == 0.5

    # Test initialization with traits
    traits = {"size": 0.8, "is_female": True, "attack": 0.2}
    genome2 = Genome(traits)
    assert genome2.traits["size"] == 0.8
    assert genome2.traits["is_female"] is True
    assert genome2.traits["attack"] == 0.2


def test_genome_constraints() -> None:
    """Tests that float traits are constrained to [0, 1]."""
    genome = Genome(
        {"size": 2.0, "extra_trait": -0.5, "is_female": False, "attack": 1.5}
    )
    assert genome.traits["size"] == 1.0
    assert genome.traits["extra_trait"] == 0.0
    assert genome.traits["is_female"] is False
    assert genome.traits["attack"] == 1.0


def test_genome_mutate() -> None:
    """Tests that mutation modifies traits independently and maintains constraints."""
    traits = {"size": 0.5, "is_female": False, "attack": 0.5}
    genome = Genome(traits)
    # High mutation rate to ensure change
    mutated = genome.mutate(mutation_rate=1.0, mutation_strength=0.2)

    # Boolean should be flipped
    assert mutated.traits["is_female"] is True
    # Float traits should be within [0, 1]
    assert 0.0 <= mutated.traits["size"] <= 1.0
    assert 0.0 <= mutated.traits["attack"] <= 1.0
    # Mutation should have happened
    assert mutated.traits["size"] != 0.5
    assert mutated.traits["attack"] != 0.5


def test_genome_crossover() -> None:
    """Tests that crossover produces a mix of independent traits correctly."""
    genome1 = Genome({"size": 0.8, "is_female": True, "attack": 0.9, "extra": 0.1})
    genome2 = Genome({"size": 0.6, "is_female": False, "attack": 0.1, "other": 0.9})

    child = genome1.crossover(genome2)

    # size should be between 0.6 and 0.8
    assert 0.6 <= child.traits["size"] <= 0.8
    # attack should be between 0.1 and 0.9
    assert 0.1 <= child.traits["attack"] <= 0.9
    # is_female should be either True or False
    assert isinstance(child.traits["is_female"], bool)
    # extra should be inherited from genome1
    assert child.traits["extra"] == 0.1
    # other should be inherited from genome2
    assert child.traits["other"] == 0.9
