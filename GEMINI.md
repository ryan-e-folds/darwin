# Project Overview: darwin

A Python-based evolutionary simulation where agents (creatures) with genetic traits navigate a 2D environment, consume food, and reproduce. The project explores basic evolutionary concepts like mutation, crossover, and survival of the fittest based on energy management.

## Key Technologies

- **Python:** >= 3.14
- **uv:** Project and dependency management.
- **pytest:** Testing framework.

## Architecture

- `src/darwin/genome.py`: Manages genetic traits, mutations, and crossovers.
- `src/darwin/creature.py`: Individual agents with energy, position, and genome-derived traits.
- `src/darwin/environment.py`: A 2D spatial grid managing populations of creatures and food sources.
- `src/darwin/evolution.py`: Orchestrates the simulation, including movement, consumption, and reproduction steps.

## Building and Running

### Running the Simulation
```python
from darwin.evolution import Evolution

evo = Evolution(width=50, height=50)
evo.seed_population(count=5, initial_traits={"speed": 0.5})
evo.run_generation(steps=1)

print(evo.stats)
```
