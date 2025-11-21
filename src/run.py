import asyncio
import argparse
import json
from datetime import datetime
from pathlib import Path
from typing import Optional
from utils import load_market_data, evaluate_route_detailed, plot_route
from ga import run_ga
from aco import AntAgent, CoordinatorAgent, PheromoneManagerAgent


def ensure_output_dir(run_id: Optional[str]):
    base_out_dir = Path(__file__).resolve().parent / "../out"
    if run_id is None:
        run_id = datetime.now().strftime("%Y%m%d_%H%M%S")
    target_dir = base_out_dir / run_id
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir, run_id


def persist_results(output_dir: Path, algorithm: str, routes: dict, fitnesses: dict, *, run_id: str, service_time: int, days: int):
    serialised_routes = {str(day): route for day, route in routes.items()}
    serialised_fitnesses = {str(day): fitness for day, fitness in fitnesses.items()}
    payload = {
        "run_id": run_id,
        "algorithm": algorithm,
        "service_time": service_time,
        "days": days,
        "routes": serialised_routes,
        "fitnesses": serialised_fitnesses
    }
    output_path = output_dir / f"{algorithm}_results.json"
    with output_path.open("w", encoding="utf-8") as fp:
        json.dump(payload, fp, indent=2)
    print(f"{algorithm.upper()} results saved to {output_path}")


def run_genetic_algorithm(markets, travel_times, service_time, days):
    """Run GA optimization."""
    print("\n" + "="*70)
    print("GENETIC ALGORITHM (DEAP)")
    print("="*70)
    
    best_route_all_days = {}
    best_fitness_all_days = {}
    
    for day in range(days):
        print("\n" + "="*70)
        print(f"Day {day + 1}")
        print("="*70)
        
        best_route, best_fitness = run_ga(
            markets=markets,
            travel_times=travel_times,
            service_time=service_time,
            population_size=150,
            generations=300,
            verbose=True,
        )
    
        print(f"GA Best Solution for day {day + 1}: {best_fitness} markets visited")
        print(best_route)
        
        best_route_all_days[day + 1] = best_route
        best_fitness_all_days[day + 1] = best_fitness
            
        markets = {key: value for key, value in markets.items() if int(key) not in best_route}
        
        print(f"Unvisited markets: {len(markets)}")
        
    return best_route_all_days, best_fitness_all_days


async def run_ant_colony_optimization(markets, travel_times, service_time, days):
    """Run ACO optimization."""
    print("\n" + "="*70)
    print("ANT COLONY OPTIMIZATION (SPADE)")
    print("="*70)
    
    best_route_all_days = {}
    best_fitness_all_days = {}
    
    for day in range(days):
        print("\n" + "="*70)
        print(f"Day {day + 1}")
        print("="*70)
        
        pheromone_mgr = PheromoneManagerAgent(
            "pheromone@localhost",
            "password123",
            num_locations=len(markets),
            markets=markets,
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
            num_iterations=5
        )
        
        await pheromone_mgr.start(auto_register=True)
        for ant in ants:
            await ant.start(auto_register=True)
        await coordinator.start(auto_register=True)
        
        while coordinator.is_alive():
            try:
                await asyncio.sleep(5)
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
            
            best_route_all_days[day + 1] = best_route
            best_fitness_all_days[day + 1] = best_fitness
            
            markets = {key: value for key, value in markets.items() if int(key) not in best_route}
            
            print(f"Unvisited markets: {len(markets)}")
            
    return best_route_all_days, best_fitness_all_days


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--service_time", type=int, default=30)
    parser.add_argument("--places_file", required=True)
    parser.add_argument("--travel_times_file", required=True)
    parser.add_argument("--algorithm", choices=["aco", "ga", "all"], required=True)
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--run_id", default=None, help="Optional identifier for this execution; defaults to timestamp")
    parser.add_argument("--plot", action="store_true", help="Plot the routes")
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
    
    output_dir, run_id = ensure_output_dir(args.run_id)
    
    if args.algorithm == "ga":
        routes, fitnesses = run_genetic_algorithm(markets, travel_times, args.service_time, args.days)
        persist_results(output_dir, "ga", routes, fitnesses, run_id=run_id, service_time=args.service_time, days=args.days)
        
        if args.plot:
            plot_route(routes, markets)
            
    elif args.algorithm == "aco":
        routes, fitnesses = asyncio.run(run_ant_colony_optimization(markets, travel_times, args.service_time, args.days))
        persist_results(output_dir, "aco", routes, fitnesses, run_id=run_id, service_time=args.service_time, days=args.days)
        
        if args.plot:
            plot_route(routes, markets)
            
    else:
        # Run GA
        ga_routes, ga_fitnesses = run_genetic_algorithm(markets, travel_times, args.service_time, args.days)
        persist_results(output_dir, "ga", ga_routes, ga_fitnesses, run_id=run_id, service_time=args.service_time, days=args.days)
        
        # Run ACO
        aco_routes, aco_fitnesses = asyncio.run(run_ant_colony_optimization(markets, travel_times, args.service_time, args.days))
        persist_results(output_dir, "aco", aco_routes, aco_fitnesses, run_id=run_id, service_time=args.service_time, days=args.days)
        
        if args.plot:
            plot_route(ga_routes, markets)
            plot_route(aco_routes, markets)

        # Compare
        print("\n" + "="*70)
        print("COMPARISON")
        print("="*70)
        total_ga = sum(ga_fitnesses.values())
        total_aco = sum(aco_fitnesses.values())
        print(f"GA:  {total_ga} markets")
        print(f"ACO: {total_aco} markets")
        print(f"Winner: {'GA' if total_ga > total_aco else 'ACO' if total_aco > total_ga else 'Tie'}")
        print("="*70)


if __name__ == "__main__":
    main()
