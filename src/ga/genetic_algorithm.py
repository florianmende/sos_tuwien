import random
import numpy as np
from deap import base, creator, tools, algorithms


def evaluate_route(individual, markets, travel_times, service_time):
    """
    Evaluate a route and return fitness (number of markets visited).
    Individual contains 0-based indices, convert to 1-based market IDs.
    """
    if not individual or len(individual) == 0:
        return (0,)
    
    # Convert 0-based indices to 1-based market IDs
    market_sequence = [idx + 1 for idx in individual]
    
    feasible_route = []
    current_time = markets[str(market_sequence[0])]["opens_minutes"]
    
    for market_id in market_sequence:
        market = markets[str(market_id)]
        
        if not feasible_route:
            arrival_time = current_time
        else:
            travel_time = travel_times[feasible_route[-1]][market_id]
            arrival_time = current_time + travel_time
        
        if arrival_time < market["opens_minutes"]:
            arrival_time = market["opens_minutes"]
        
        if arrival_time > market["closes_minutes"]:
            continue
        
        departure_time = arrival_time + service_time
        
        feasible_route.append(market_id)
        current_time = departure_time
    
    fitness = len(feasible_route)
    return (fitness,)


def get_feasible_route(individual, markets, travel_times, service_time):
    """Get the actual feasible route from an individual."""
    if not individual or len(individual) == 0:
        return []
    
    market_sequence = [idx + 1 for idx in individual]
    
    feasible_route = []
    current_time = markets[str(market_sequence[0])]["opens_minutes"]
    
    for market_id in market_sequence:
        market = markets[str(market_id)]
        
        if not feasible_route:
            arrival_time = current_time
        else:
            travel_time = travel_times[feasible_route[-1]][market_id]
            arrival_time = current_time + service_time + travel_time
        
        if arrival_time < market["opens_minutes"]:
            arrival_time = market["opens_minutes"]
        
        if arrival_time > market["closes_minutes"]:
            continue
        
        feasible_route.append(market_id)
        current_time = arrival_time
    
    return feasible_route


def run_ga(markets, travel_times, service_time=30,
           population_size=100, generations=300, verbose=True):
    """
    Run genetic algorithm for market route optimization.
    
    Returns:
        (best_route, best_fitness)
    """
    # DEAP Setup
    creator.create("FitnessMax", base.Fitness, weights=(1.0,))
    creator.create("Individual", list, fitness=creator.FitnessMax)
    
    toolbox = base.Toolbox()
    
    num_markets = len(markets)
    market_indices = list(range(num_markets))
    
    toolbox.register("indices", random.sample, market_indices, num_markets)
    toolbox.register("individual", tools.initIterate, creator.Individual, toolbox.indices)
    toolbox.register("population", tools.initRepeat, list, toolbox.individual)
    toolbox.register("mate", tools.cxOrdered)
    toolbox.register("mutate", tools.mutShuffleIndexes, indpb=0.1)
    toolbox.register("select", tools.selTournament, tournsize=3)
    toolbox.register(
        "evaluate",
        evaluate_route,
        markets=markets,
        travel_times=travel_times,
        service_time=service_time
    )
    
    # Create initial population
    population = toolbox.population(n=population_size)
    hof = tools.HallOfFame(1)
    
    stats = tools.Statistics(lambda ind: ind.fitness.values)
    stats.register("avg", np.mean)
    stats.register("std", np.std)
    stats.register("min", np.min)
    stats.register("max", np.max)
    
    # Run algorithm
    population, logbook = algorithms.eaSimple(
        population,
        toolbox,
        cxpb=0.7,
        mutpb=0.2,
        ngen=generations,
        stats=stats,
        halloffame=hof,
        verbose=verbose
    )
    
    # Get best solution
    best_individual = hof[0]
    best_fitness = int(best_individual.fitness.values[0])
    best_route = get_feasible_route(
        best_individual,
        markets,
        travel_times,
        service_time
    )
    
    return best_route, best_fitness
