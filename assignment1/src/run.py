import asyncio
import itertools
import json
import sys
import os
import contextlib
import argparse
from datetime import datetime
from pathlib import Path
from tqdm import tqdm

from find_solution import run_ant_colony_optimization, run_genetic_algorithm
from utils import load_market_data

# parameter grids
GA_GRID = {
    "population_size": [300, 500, 800],
    "generations": [300, 500],
    "cxpb": [0.6, 0.7, 0.8],
    "mutpb": [0.1, 0.2, 0.3],
    "tournsize": [3, 5],
    "indpb": [0.05, 0.1, 0.2]
}

ACO_GRID = {
    "num_ants": [20, 40],
    "num_iterations": [5, 10, 15],
    "initial_pheromone": [1.0],
    "decay": [0.3, 0.5, 0.7],
    "alpha": [1.0, 1.5],
    "beta": [2.0, 3.0, 4.0],
    "reward_multiplier": [2.0, 5.0]
}

# suppress unwanted stdout outputs
@contextlib.contextmanager
def suppress_stdout():
    with open(os.devnull, "w") as devnull:
        old_stdout = sys.stdout
        sys.stdout = devnull
        try:
            yield
        finally:
            sys.stdout = old_stdout

def generate_combinations(grid):
    keys, values = zip(*grid.items())
    return [dict(zip(keys, v)) for v in itertools.product(*values)]

async def run_grid_search(args):
    run_id = datetime.now().strftime("%Y%m%d_%H%M%S_GRID")
    output_dir = Path("out") / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    print(f"--- GRID SEARCH: {args.algorithm.upper()} ---")
    print(f"Output Directory: {output_dir}")

    markets, travel_times = load_market_data(args.places_file, args.travel_times_file, mode="walking")
    
    grid = GA_GRID if args.algorithm == "ga" else ACO_GRID
    combinations = generate_combinations(grid)
    
    print(f"Combinations: {len(combinations)}")
    
    results = []

    for params in tqdm(combinations, unit="run"):
        entry = {
            "parameters": params,
            "timestamp": datetime.now().isoformat(),
            "success": False,
            "total_score": 0,
            "routes": {},
            "fitness_per_day": {}
        }

        try:
            with suppress_stdout():
                if args.algorithm == "ga":
                    routes, fitnesses = run_genetic_algorithm(
                        markets=markets,
                        travel_times=travel_times,
                        service_time=args.service_time,
                        days=args.days,
                        params=params
                    )
                else:
                    routes, fitnesses = await run_ant_colony_optimization(
                        markets=markets,
                        travel_times=travel_times,
                        service_time=args.service_time,
                        days=args.days,
                        params=params,
                        output_dir=None 
                    )

            # Serialize keys (days) to strings for JSON compliance
            entry["routes"] = {str(k): v for k, v in routes.items()}
            entry["fitness_per_day"] = {str(k): v for k, v in fitnesses.items()}
            entry["total_score"] = sum(fitnesses.values())
            entry["success"] = True

        except Exception as e:
            entry["error"] = str(e)

        results.append(entry)
        
        # Slight delay for ACO cleanup
        if args.algorithm == "aco":
            await asyncio.sleep(0.1)

    # 1. Save all results
    full_path = output_dir / f"{args.algorithm}_all_results.json"
    with open(full_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\nAll results saved to: {full_path}")

    # 2. Save best result separately
    successful_runs = [r for r in results if r["success"]]
    if successful_runs:
        best_run = max(successful_runs, key=lambda x: x['total_score'])
        best_path = output_dir / f"{args.algorithm}_best_run.json"
        with open(best_path, "w") as f:
            json.dump(best_run, f, indent=2)
        print(f"Best run ({best_run['total_score']} markets) saved to: {best_path}")
    else:
        print("No successful runs recorded.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--places_file", required=True)
    parser.add_argument("--travel_times_file", required=True)
    parser.add_argument("--algorithm", choices=["aco", "ga"], required=True)
    parser.add_argument("--days", type=int, default=1)
    parser.add_argument("--service_time", type=int, default=30)
    
    args = parser.parse_args()
    asyncio.run(run_grid_search(args))