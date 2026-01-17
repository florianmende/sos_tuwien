def format_time(minutes):
    """Convert minutes since midnight to HH:MM format."""
    hours = minutes // 60
    mins = minutes % 60
    return f"{hours:02d}:{mins:02d}"


def evaluate_route_detailed(tour, markets, travel_times, start_time=600, service_time=30):
    """Print detailed route evaluation with timing breakdown."""
    if not tour or len(tour) == 0:
        print("No route to evaluate")
        return
    
    print("\n" + "="*70)
    print("DETAILED ROUTE EVALUATION")
    print("="*70)
    
    current_time = max(start_time, markets[str(tour[0])]["opens_minutes"])
    total_travel = 0
    total_waiting = 0
    total_service = 0
    
    for idx, market_id in enumerate(tour):
        market = markets[str(market_id)]
        
        if idx == 0:
            arrival = current_time
            travel = 0
            waiting = 0
        else:
            prev_id = tour[idx - 1]
            travel = travel_times[prev_id][market_id]
            arrival = current_time + travel
            
            if arrival < market["opens_minutes"]:
                waiting = market["opens_minutes"] - arrival
                arrival = market["opens_minutes"]
            else:
                waiting = 0
            
            total_travel += travel
            total_waiting += waiting
        
        departure = arrival + service_time
        current_time = departure
        total_service += service_time
        
        print(f"\n{'='*70}")
        print(f"Market #{idx + 1}: {market['Name']} (ID: {market_id})")
        print(f"{'='*70}")
        print(f"    Opening hours: {market['Opens']} - {market['Closes']}")
        
        if idx > 0:
            print(f"    Travel time from previous market: {travel} minutes")
            if waiting > 0:
                print(f"    Waiting time (market closed): {waiting} minutes")
        
        print(f"    Arrive at market: {format_time(arrival)}")
        print(f"    Leave market: {format_time(departure)}")
        print(f"    Time spent at market: {service_time} minutes")
    
    first_arrival = max(start_time, markets[str(tour[0])]["opens_minutes"])
    
    print("\n" + "="*70)
    print("ROUTE SUMMARY")
    print("="*70)
    print(f"Total markets visited: {len(tour)}")
    print(f"Start market: {markets[str(tour[0])]['Name']} (ID: {tour[0]})")
    print(f"End market: {markets[str(tour[-1])]['Name']} (ID: {tour[-1]})")
    print(f"\nStart time: {format_time(first_arrival)}")
    print(f"End time: {format_time(current_time)}")
    print(f"Total duration: {current_time - first_arrival} minutes "
          f"({(current_time - first_arrival) / 60:.1f} hours)")
    print(f"\nTime breakdown:")
    print(f"    Service time (at markets): {total_service} minutes")
    print(f"    Travel time (between markets): {total_travel} minutes")
    print(f"    Waiting time (before opening): {total_waiting} minutes")
    print(f"    Total: {total_service + total_travel + total_waiting} minutes")
    print("="*70 + "\n")
