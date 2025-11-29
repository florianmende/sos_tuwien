import json
import statistics
import os
import datetime
from collections import defaultdict
import sys

def load_data(filename):
    """Loads the JSON data from the file."""
    if not os.path.exists(filename):
        print(f"File '{filename}' not found.")
        return None
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        print(f"Error: {filename} contains invalid JSON.")
        return []

def analyze_results(data):
    """Calculates and prints statistics including timing analysis."""
    if not data:
        print("No data to analyze.")
        return

    valid_data = []
    for d in data:
        if 'parameters' not in d or 'total_score' not in d:
            continue
        
        # Parse timestamp immediately for sorting
        try:
            d['_dt'] = datetime.datetime.fromisoformat(d.get('timestamp', ''))
            valid_data.append(d)
        except (ValueError, TypeError):
            continue

    if len(valid_data) < len(data):
        print(f"Warning: Skipped {len(data) - len(valid_data)} malformed/untimestamped entries.")

    total_runs = len(valid_data)
    
    valid_data.sort(key=lambda x: x['_dt'])

    all_durations = []
    for i in range(total_runs - 1):
        diff = valid_data[i+1]['_dt'] - valid_data[i]['_dt']
        seconds = diff.total_seconds()
        valid_data[i]['_duration'] = seconds
        all_durations.append(seconds)

    # Global Stats
    successes = [d for d in valid_data if d.get('success', False)]
    scores = [d.get('total_score', 0) for d in valid_data]

    print(f"{'='*50}")
    print(f"OPTIMIZATION STATISTICS ({total_runs} Valid Runs)")
    print(f"{'='*50}")

    success_rate = (len(successes) / total_runs) * 100 if total_runs > 0 else 0
    print(f"Success Rate:   {success_rate:.2f}%")

    if scores:
        print(f"Mean Score:     {statistics.mean(scores):.2f}")
        print(f"Max Score:      {max(scores)}")

    if all_durations:
        print(f"Mean Time/Run:  {statistics.mean(all_durations):.2f}s")
        print(f"Total Duration: {sum(all_durations):.2f}s")

    # Group by Parameters
    config_stats = defaultdict(lambda: {'scores': [], 'times': []})

    for entry in valid_data:
        params = entry.get('parameters', {})
        param_key = tuple(sorted(params.items()))
        
        config_stats[param_key]['scores'].append(entry.get('total_score', 0))
        
        if '_duration' in entry:
            config_stats[param_key]['times'].append(entry['_duration'])

    # Process Aggregates
    final_configs = []
    for param_key, stats in config_stats.items():
        avg_score = statistics.mean(stats['scores'])
        avg_time = statistics.mean(stats['times']) if stats['times'] else float('inf')
        count = len(stats['scores'])
        final_configs.append({
            'params': dict(param_key),
            'avg_score': avg_score,
            'avg_time': avg_time,
            'count': count
        })

    # top 3 score
    final_configs.sort(key=lambda x: x['avg_score'], reverse=True)
    
    print(f"\n{'-'*20}\nTOP 3 BY SCORE\n{'-'*20}")
    for i, cfg in enumerate(final_configs[:3], 1):
        time_str = f"{cfg['avg_time']:.2f}s" if cfg['avg_time'] != float('inf') else "N/A"
        print(f"#{i} Score: {cfg['avg_score']:.2f} | Time: {time_str} | Samples: {cfg['count']}")
        param_str = ", ".join([f"{k}={v}" for k, v in cfg['params'].items()])
        print(f"   Params: {param_str}")

    # top 3 walltime
    timed_configs = [c for c in final_configs if c['avg_time'] != float('inf')]
    timed_configs.sort(key=lambda x: x['avg_time'])

    print(f"\n{'-'*20}\nTOP 3 BY TIME (FASTEST)\n{'-'*20}")
    if not timed_configs:
        print("Not enough data points to calculate per-run duration.")
    else:
        for i, cfg in enumerate(timed_configs[:3], 1):
            print(f"#{i} Time: {cfg['avg_time']:.2f}s | Score: {cfg['avg_score']:.2f} | Samples: {cfg['count']}")
            param_str = ", ".join([f"{k}={v}" for k, v in cfg['params'].items()])
            print(f"   Params: {param_str}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python script_name.py <filename.json>")
    else:
        target_file = sys.argv[1]
        data_content = load_data(target_file)
        if data_content:
            analyze_results(data_content)