import random
import numpy as np
import json
import uuid
import asyncio
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template


class AntAgent(Agent):
    """
    An ACO ant agent that constructs paths to maximize markets visited.
    """
    
    def __init__(self, jid, password, ant_id, markets, travel_times, 
                 manager_jid, coordinator_jid=None, service_time=30, alpha=1.0, beta=2.0):
        super().__init__(jid, password)
        self.ant_id = ant_id
        self.markets = markets
        self.travel_times = travel_times
        self.manager_jid = manager_jid
        self.coordinator_jid = coordinator_jid or "coordinator@localhost"
        self.service_time = service_time
        
        self.alpha = alpha
        self.beta = beta
        
        self.current_tour = []
        self.current_time = 0
        self.current_location = None
    
    async def setup(self):
        print(f"[Ant {self.ant_id}] Starting at {self.jid}")
        # Store reference to tour construction behavior on agent
        tour_behavior = self.TourConstructionBehavior()
        self.tour_behavior = tour_behavior
        # Add behavior to handle start_iteration messages separately
        template = Template()
        template.set_metadata("performative", "start_iteration")
        self.add_behaviour(self.StartIterationBehavior(), template)
        # Main tour construction behavior
        self.add_behaviour(tour_behavior)
    
    class StartIterationBehavior(CyclicBehaviour):
        """Handles start_iteration messages from coordinator"""
        async def run(self):
            try:
                msg = await self.receive(timeout=1)
            except asyncio.CancelledError:
                return
            if msg: 
                try:
                    data = json.loads(msg.body)
                    iteration_id = data.get("iteration_id")
                    # Update tour construction behavior's iteration via agent reference
                    if hasattr(self.agent, 'tour_behavior') and self.agent.tour_behavior:
                        if iteration_id > self.agent.tour_behavior.current_iteration:
                            self.agent.tour_behavior.current_iteration = iteration_id
                            self.agent.tour_behavior.reset_tour()
                except (json.JSONDecodeError, KeyError, TypeError):
                    # Invalid message, ignore
                    pass


    class TourConstructionBehavior(CyclicBehaviour):
        
        async def on_start(self):
            self.current_iteration = 0
            # Don't start tour automatically - wait for start_iteration signal
            self.tour_complete = True  # Mark as complete so we wait for signal
        
        def reset_tour(self):
            """Reset ant state for a new tour"""
            # Start at a random market
            all_locations = [int(key) for key in self.agent.markets.keys()]
            start = random.choice(all_locations)
            
            self.agent.current_tour = [start]
            
            # Always start at the opening time of the first market
            # (ants arrive exactly when the market opens)
            market = self.agent.markets[str(start)]
            arrival_time = market["opens_minutes"]
            
            # After service at first market, departure time
            departure_time = arrival_time + self.agent.service_time
            self.agent.current_time = departure_time  # Set to departure time for consistency
            
            self.agent.current_location = start
            
            # All other locations are unvisited
            self.unvisited = set(all_locations)
            self.unvisited.remove(start)
            
            self.tour_complete = False
        
        async def run(self):
            # If tour is complete, just wait (start_iteration is handled by separate behavior)
            if self.tour_complete:
                await asyncio.sleep(0.1)  # Small delay to avoid busy waiting
                return
            
            next_location = await self.select_next_market()
            
            if next_location is None:
                self.tour_complete = True
                await self.deposit_tour()
                # Send tour_complete message to coordinator
                await self.notify_tour_complete()
                return
            
            # Calculate travel and arrival time
            travel_time = self.agent.travel_times[
                self.agent.current_location
            ][next_location]
            
            arrival_time = self.agent.current_time + travel_time
            market = self.agent.markets[str(next_location)]
            open_time = market["opens_minutes"]
            close_time = market["closes_minutes"]
            
            # Wait if arrive before opening
            if arrival_time < open_time:
                arrival_time = open_time
            
            # Ensure we can complete service before market closes
            departure_time = arrival_time + self.agent.service_time
            if departure_time > close_time:
                # Can't complete service before closing, skip this market
                # This shouldn't happen but add safety check
                self.tour_complete = True
                await self.deposit_tour()
                await self.notify_tour_complete()
                return
            
            self.agent.current_tour.append(next_location)
            self.agent.current_time = departure_time
            self.agent.current_location = next_location
            self.unvisited.remove(next_location)
        
        async def select_next_market(self):
            if not self.unvisited:
                return None
            
            probabilities = {}
            feasible_cities = []
            
            for next_city in self.unvisited:
                travel_time = self.agent.travel_times[
                    self.agent.current_location
                ][next_city]
                # current_time represents departure time from current location
                # So arrival at next market = departure + travel_time
                arrival_time = self.agent.current_time + travel_time
                
                market = self.agent.markets[str(next_city)]
                open_time = market["opens_minutes"]
                close_time = market["closes_minutes"]
                
                # Adjust arrival if before opening
                if arrival_time < open_time:
                    arrival_time = open_time
                
                # Skip if we can't complete service before market closes
                # Need at least service_time available: arrival + service_time <= close_time
                departure_time = arrival_time + self.agent.service_time
                if departure_time > close_time:
                    continue
                
                feasible_cities.append(next_city)
                
                pheromone = await self.query_pheromone(
                    self.agent.current_location,
                    next_city
                )
                
                distance = self.agent.travel_times[
                    self.agent.current_location
                ][next_city]
                heuristic = 1.0 / (distance + 1)
                
                probability = (
                    (pheromone ** self.agent.alpha) *
                    (heuristic ** self.agent.beta)
                )
                probabilities[next_city] = probability
            
            if not feasible_cities:
                return None
            
            total = sum(probabilities.values())
            if total == 0:
                return random.choice(feasible_cities)
            
            normalized = {
                city: prob / total 
                for city, prob in probabilities.items()
            }
            
            cities_list = list(feasible_cities)
            probabilities_list = [
                normalized[city] for city in cities_list
            ]
            
            selected = np.random.choice(
                cities_list,
                p=probabilities_list
            )
            
            return int(selected)
        
        async def query_pheromone(self, from_loc, to_loc):
            # Generate unique correlation ID for request-response matching
            correlation_id = str(uuid.uuid4())
            
            query_msg = Message(to=self.agent.manager_jid)
            query_msg.body = json.dumps({
                "from": from_loc,
                "to": to_loc,
                "correlation_id": correlation_id
            })
            query_msg.set_metadata("performative", "query_pheromone")
            query_msg.set_metadata("correlation_id", correlation_id)
            
            await self.send(query_msg)
            
            # Manually filter for matching response with correlation ID
            # Keep receiving until we get the matching response or timeout
            start_time = asyncio.get_event_loop().time()
            timeout = 5
            
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                remaining = timeout - elapsed
                if remaining <= 0:
                    return 1.0
                
                response = await self.receive(timeout=min(remaining, 0.1))
                
                if response is None:
                    # Timeout reached
                    return 1.0
                
                # Check if this is the response we're waiting for
                if (response.get_metadata("performative") == "pheromone_response" and
                    response.get_metadata("correlation_id") == correlation_id):
                    try:
                        data = json.loads(response.body)
                        # Verify correlation ID matches in body too
                        if data.get("correlation_id") == correlation_id:
                            return data.get("pheromone", 1.0)
                        else:
                            return 1.0
                    except (json.JSONDecodeError, KeyError):
                        return 1.0
                # Not our message, continue waiting
        
        async def deposit_tour(self):
            
            msg = Message(to=self.agent.manager_jid)
            
            # All locations in tour are visited markets
            markets_visited = len(self.agent.current_tour)
            
            msg.body = json.dumps({
                "tour": self.agent.current_tour,
                "num_markets": markets_visited,
                "iteration_id": self.current_iteration,
                "ant_id": self.agent.ant_id
            })
            msg.set_metadata("performative", "deposit_pheromone")
            
            await self.send(msg)
        
        async def notify_tour_complete(self):
            """Notify coordinator that tour is complete"""
            msg = Message(to=self.agent.coordinator_jid)
            msg.body = json.dumps({
                "ant_id": self.agent.ant_id,
                "iteration_id": self.current_iteration
            })
            msg.set_metadata("performative", "tour_complete")
            
            await self.send(msg)
