import random
import numpy as np
import json
from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.message import Message
from spade.template import Template


class AntAgent(Agent):
    """
    An ACO ant agent that constructs paths to maximize markets visited.
    """
    
    def __init__(self, jid, password, ant_id, markets, travel_times, 
                 manager_jid, service_time=30):
        super().__init__(jid, password)
        self.ant_id = ant_id
        self.markets = markets
        self.travel_times = travel_times
        self.manager_jid = manager_jid
        self.service_time = service_time
        
        self.alpha = 1.0
        self.beta = 2.0
        
        self.current_tour = []
        self.current_time = 0
        self.current_location = None
    
    async def setup(self):
        print(f"[Ant {self.ant_id}] Starting at {self.jid}")
        self.add_behaviour(self.TourConstructionBehavior())


    class TourConstructionBehavior(CyclicBehaviour):
        
        async def on_start(self):
            self.reset_tour()
        
        def reset_tour(self):
            """Reset ant state for a new tour"""
            # Start at a random market
            all_locations = [int(key) for key in self.agent.markets.keys()]
            start = random.choice(all_locations)
            
            self.agent.current_tour = [start]
            
            # Initialize time to the LATER of: start_time or market opening
            market = self.agent.markets[str(start)]
            self.agent.current_time = market["opens_minutes"]
            
            self.agent.current_location = start
            
            # All other locations are unvisited
            self.unvisited = set(all_locations)
            self.unvisited.remove(start)
            
            self.tour_complete = False
        
        async def run(self):
            # Check for coordinator signal to start new iteration
            if self.tour_complete:
                msg = await self.receive(timeout=1)
                if msg and msg.get_metadata("performative") == "start_iteration":
                    self.reset_tour()
                return
            
            next_location = await self.select_next_market()
            
            if next_location is None:
                self.tour_complete = True
                await self.deposit_tour()
                return
            
            # Calculate travel and arrival time
            travel_time = self.agent.travel_times[
                self.agent.current_location
            ][next_location]
            
            arrival_time = self.agent.current_time + travel_time
            market = self.agent.markets[str(next_location)]
            open_time = market["opens_minutes"]
            
            # Wait if arrive before opening
            if arrival_time < open_time:
                arrival_time = open_time
            
            departure_time = arrival_time + self.agent.service_time
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
                arrival_time = self.agent.current_time + self.agent.service_time + travel_time
                
                market = self.agent.markets[str(next_city)]
                open_time = market["opens_minutes"]
                close_time = market["closes_minutes"]
                
                # Adjust arrival if before opening
                if arrival_time < open_time:
                    arrival_time = open_time
                
                # Skip if we'd arrive after closing
                if arrival_time > close_time:
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
            query_msg = Message(to=self.agent.manager_jid)
            query_msg.body = json.dumps({
                "from": from_loc,
                "to": to_loc
            })
            query_msg.set_metadata("performative", "query_pheromone")
            
            await self.send(query_msg)
            
            response = await self.receive(timeout=5)
            
            if response is None:
                return 1.0
            
            data = json.loads(response.body)
            return data.get("pheromone", 1.0)
        
        async def deposit_tour(self):
            # No need to append end location - tour is complete as-is
            
            msg = Message(to=self.agent.manager_jid)
            
            # All locations in tour are visited markets
            markets_visited = len(self.agent.current_tour)
            
            msg.body = json.dumps({
                "tour": self.agent.current_tour,
                "num_markets": markets_visited
            })
            msg.set_metadata("performative", "deposit_pheromone")
            
            await self.send(msg)
