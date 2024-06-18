import requests
import pandas as pd
import random
from collections import defaultdict


# Function to fetch race results
def fetch_race_results(season):
    url = f"http://ergast.com/api/f1/{season}/results.json?limit=1000"
    response = requests.get(url)
    data = response.json()
    races = data["MRData"]["RaceTable"]["Races"]
    results = []

    for race in races:
        race_name = race["raceName"]
        round_number = int(race["round"])
        for result in race["Results"]:
            driver = result["Driver"]["driverId"]
            position = int(result["position"])
            results.append(
                {
                    "season": season,
                    "round": round_number,
                    "race_name": race_name,
                    "driver": driver,
                    "position": position,
                }
            )

    return results


# Function to apply a scoring system
def apply_scoring_system(results, scoring_system):
    points_table = defaultdict(int)
    leader_changes = 0
    last_leader = None

    for race in results:
        points = scoring_system.get(race["position"], 0)
        points_table[race["driver"]] += points

        # Determine the current leader
        current_leader = max(points_table, key=points_table.get)
        if current_leader != last_leader:
            leader_changes += 1
            last_leader = current_leader

    return leader_changes


# Genetic Algorithm Functions


# Generate initial population
def generate_population(size, num_positions):
    population = []
    for _ in range(size):
        scoring_system = {}

        for i in range(num_positions):
            scoring_system[i + 1] = random.randint(
                10 - i,
                (
                    min(scoring_system.values()) - 1
                    if len(scoring_system.keys()) > 0
                    else 50
                ),
            )

        population.append(scoring_system)
    return population


# Evaluate fitness of each individual
def evaluate_population(population, results):
    fitness_scores = []
    for scoring_system in population:
        leader_changes = apply_scoring_system(results, scoring_system)
        fitness_scores.append((scoring_system, leader_changes))
    return fitness_scores


# Select parents
def select_parents(fitness_scores, num_parents):
    fitness_scores.sort(key=lambda x: x[1], reverse=True)
    return [scoring_system for scoring_system, _ in fitness_scores[:num_parents]]


# Crossover
def crossover(parents, num_offspring, num_positions):
    offspring = []
    for _ in range(num_offspring):
        parent1 = random.choice(parents)
        parent2 = random.choice(parents)

        child = {}
        for pos in range(1, num_positions + 1):
            if len(child.keys()) > 0 and parent1[pos] >= min(child.values()):
                child[pos] = parent2[pos]
            elif len(child.keys()) > 0 and parent2[pos] >= min(child.values()):
                child[pos] = parent1[pos]
            else:
                child[pos] = parent1[pos] if (random.random() > 0.5) else parent2[pos]

        offspring.append(child)
    return offspring


# Mutation
def mutate(offspring, mutation_rate, num_positions):
    for scoring_system in offspring:
        for pos in range(2, num_positions):
            if random.random() < mutation_rate:
                scoring_system[pos] = random.randint(
                    scoring_system[pos + 1] + 1, scoring_system[pos - 1] - 1
                )
    return offspring


# Main Genetic Algorithm
def genetic_algorithm(
    results, num_generations, population_size, num_positions, num_parents, mutation_rate
):

    print("Generate population")
    population = generate_population(population_size, num_positions)

    for gen_id in range(num_generations):
        print(f"generation {gen_id}")
        fitness_scores = evaluate_population(population, results)
        parents = select_parents(fitness_scores, num_parents)
        offspring = crossover(parents, population_size - num_parents, num_positions)
        offspring = mutate(offspring, mutation_rate, num_positions)
        population = parents + offspring

    # Final evaluation
    fitness_scores = evaluate_population(population, results)
    best_scoring_system, best_score = max(fitness_scores, key=lambda x: x[1])
    return best_scoring_system, best_score


# Evaluate the current scoring system
def evaluate_current_system(results):
    current_scoring_system = {
        1: 25,
        2: 18,
        3: 15,
        4: 12,
        5: 10,
        6: 8,
        7: 6,
        8: 4,
        9: 2,
        10: 1,
    }
    leader_changes = apply_scoring_system(results, current_scoring_system)
    return current_scoring_system, leader_changes


# Fetch race results for a given range of seasons
seasons = range(2010, 2024)  # Adjust range as needed
all_results = []
for season in seasons:
    all_results.extend(fetch_race_results(season))

# Parameters for the Genetic Algorithm
num_generations = 100
population_size = 200
num_positions = 10  # Assuming we want to assign points to the top 10 positions
num_parents = 10
mutation_rate = 0.1

# Run the Genetic Algorithm
best_scoring_system, best_score = genetic_algorithm(
    all_results,
    num_generations,
    population_size,
    num_positions,
    num_parents,
    mutation_rate,
)

# Evaluate the current scoring system
current_scoring_system, current_leader_changes = evaluate_current_system(all_results)

print(f"Best Scoring System: {best_scoring_system}")
print(f"Number of Leader Changes (Best): {best_score}")
print(f"Current Scoring System: {current_scoring_system}")
print(f"Number of Leader Changes (Current): {current_leader_changes}")
