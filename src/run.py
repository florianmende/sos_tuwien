import asyncio
import argparse
from utils import load_market_data, evaluate_route_detailed
from ga import run_ga
from aco import AntAgent, CoordinatorAgent, PheromoneManagerAgent


def run_genetic_algorithm(markets, travel_times, service_time):
    """Run GA optimization."""
    print("\n" + "="*70)
    print("GENETIC ALGORITHM (DEAP)")
    print("="*70)
    
    best_route, best_fitness = run_ga(
        markets=markets,
        travel_times=travel_times,
        service_time=service_time,
        population_size=100,
        generations=300,
        verbose=True
    )
    
    print(f"GA Best Solution: {best_fitness} markets visited")
    
    print(best_route)
    
    if best_route:
        evaluate_route_detailed(best_route, markets, travel_times, service_time=service_time)
    
    return best_route, best_fitness


async def run_ant_colony_optimization(markets, travel_times, service_time):
    """Run ACO optimization."""
    print("\n" + "="*70)
    print("ANT COLONY OPTIMIZATION (SPADE)")
    print("="*70)
    
    pheromone_mgr = PheromoneManagerAgent(
        "pheromone@localhost",
        "password123",
        num_locations=len(markets),
        initial_pheromone=1.0,
        decay=0.5
    )
    
    num_ants = 20
    ants = []
    for i in range(num_ants):
        ant = AntAgent(
            f"ant_{i}@localhost",
            f"password{i}",
            ant_id=i,
            markets=markets,
            travel_times=travel_times,
            manager_jid=str(pheromone_mgr.jid),
            service_time=service_time
        )
        ants.append(ant)
    
    ant_jids = [str(ant.jid) for ant in ants]
    coordinator = CoordinatorAgent(
        "coordinator@localhost",
        "password123",
        pheromone_manager_jid=str(pheromone_mgr.jid),
        ant_jids=ant_jids,
        num_iterations=10
    )
    
    await pheromone_mgr.start(auto_register=True)
    for ant in ants:
        await ant.start(auto_register=True)
    await coordinator.start(auto_register=True)
    
    while coordinator.is_alive():
        try:
            await asyncio.sleep(1)
        except KeyboardInterrupt:
            break
    
    await coordinator.stop()
    for ant in ants:
        await ant.stop()
    await pheromone_mgr.stop()
    
    best_solution = coordinator.best_solution
    if best_solution:
        best_route = best_solution.get('best_tour', [])
        best_fitness = best_solution.get('best_count', 0)
        
        print(f"ACO Best Solution: {best_fitness} markets visited")
        
        if best_route:
            evaluate_route_detailed(best_route, markets, travel_times, service_time=service_time)
        
        return best_route, best_fitness
    
    return None, 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--service_time", type=int, default=30)
    parser.add_argument("--places_file", required=True)
    parser.add_argument("--travel_times_file", required=True)
    parser.add_argument("--algorithm", choices=["aco", "ga", "all"], required=True)
    args = parser.parse_args()
    
    # Load data
    markets, travel_times = load_market_data(
        args.places_file,
        args.travel_times_file,
        mode="walking"
    )
    
    print(f"\n{'='*70}")
    print(f"MARKET ROUTE OPTIMIZATION")
    print(f"{'='*70}")
    print(f"Markets: {len(markets)}")
    print(f"Service time: {args.service_time} minutes per market")
    print(f"{'='*70}\n")
    
    if args.algorithm == "ga":
        run_genetic_algorithm(markets, travel_times, args.service_time)
    
    elif args.algorithm == "aco":
        asyncio.run(run_ant_colony_optimization(markets, travel_times, args.service_time))
    
    else:
        # Run GA
        ga_route, ga_fitness = run_genetic_algorithm(markets, travel_times, args.service_time)
        
        # Run ACO
        aco_route, aco_fitness = asyncio.run(run_ant_colony_optimization(markets, travel_times, args.service_time))
        
        # Compare
        print("\n" + "="*70)
        print("COMPARISON")
        print("="*70)
        print(f"GA:  {ga_fitness} markets")
        print(f"ACO: {aco_fitness} markets")
        print(f"Winner: {'GA' if ga_fitness > aco_fitness else 'ACO' if aco_fitness > ga_fitness else 'Tie'}")
        print("="*70)


if __name__ == "__main__":
    main()
