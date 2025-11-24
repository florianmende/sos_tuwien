import asyncio
import json
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour, CyclicBehaviour
from spade.message import Message
from spade.template import Template


class CoordinatorAgent(Agent):
    """
    Coordinator that manages the overall ACO algorithm.
    """
    
    def __init__(self, jid, password, pheromone_manager_jid, ant_jids,
                 num_iterations=100):
        super().__init__(jid, password)
        self.pheromone_manager_jid = pheromone_manager_jid
        self.ant_jids = ant_jids
        self.num_iterations = num_iterations
        self.iteration = 0
        self.best_solution = None
        self.completed_ants = set()  # Track which ants have completed their tours
    
    async def setup(self):
        print(f"[Coordinator] Starting ACO algorithm")
        self.add_behaviour(self.CoordinationBehavior(period=5))
        
        # Separate behavior to handle tour_complete messages
        template = Template()
        template.set_metadata("performative", "tour_complete")
        self.add_behaviour(self.TourCompleteBehavior(), template)
    
    class TourCompleteBehavior(CyclicBehaviour):
        """Tracks tour completion messages from ants"""
        async def run(self):
            try:
                msg = await self.receive(timeout=1)
            except asyncio.CancelledError:
                return
            if msg:
                try:
                    data = json.loads(msg.body)
                    ant_id = data.get("ant_id")
                    iteration_id = data.get("iteration_id")
                    
                    # Only track completions for current iteration
                    if iteration_id == self.agent.iteration:
                        if ant_id not in self.agent.completed_ants:
                            self.agent.completed_ants.add(ant_id)
                            print(f"[Coordinator] Ant {ant_id} completed tour for iteration {iteration_id}")
                except (json.JSONDecodeError, KeyError):
                    # Invalid message, ignore
                    pass
    
    class CoordinationBehavior(PeriodicBehaviour):
        
        async def run(self):
            self.agent.iteration += 1
            
            print(f"\n=== ACO Iteration {self.agent.iteration} ===")
            
            # Reset completion tracking for new iteration
            self.agent.completed_ants = set()
            
            # Signal all ants to start new iteration with iteration ID
            for ant_jid in self.agent.ant_jids:
                msg = Message(to=ant_jid)
                msg.set_metadata("performative", "start_iteration")
                msg.body = json.dumps({
                    "iteration_id": self.agent.iteration
                })
                await self.send(msg)
            
            # Wait for all ants to finish their tours (explicit completion tracking)
            print(f"[Coordinator] Waiting for {len(self.agent.ant_jids)} ants to complete...")
            max_wait_time = 30  # Maximum wait time in seconds
            wait_interval = 0.5  # Check every 0.5 seconds
            elapsed_time = 0
            
            while len(self.agent.completed_ants) < len(self.agent.ant_jids) and elapsed_time < max_wait_time:
                await asyncio.sleep(wait_interval)
                elapsed_time += wait_interval
            
            if len(self.agent.completed_ants) < len(self.agent.ant_jids):
                print(f"[Coordinator] Warning: Only {len(self.agent.completed_ants)}/{len(self.agent.ant_jids)} ants completed within timeout")
            else:
                print(f"[Coordinator] All {len(self.agent.completed_ants)} ants completed their tours")
            
            # Signal pheromone manager to update pheromones with iteration ID
            msg = Message(to=self.agent.pheromone_manager_jid)
            msg.set_metadata("performative", "end_iteration")
            msg.body = json.dumps({
                "iteration_id": self.agent.iteration
            })
            await self.send(msg)
            
            # Wait for pheromone update acknowledgment (explicit wait)
            # Manually filter for iteration_updated messages
            start_time = asyncio.get_event_loop().time()
            timeout = 5
            response = None
            
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                remaining = timeout - elapsed
                if remaining <= 0:
                    break
                
                msg = await self.receive(timeout=min(remaining, 0.1))
                if msg and msg.get_metadata("performative") == "iteration_updated":
                    response = msg
                    break
            
            if response:
                try:
                    data = json.loads(response.body)
                    iteration_id = data.get("iteration_id")
                    if iteration_id == self.agent.iteration:
                        print(f"[Coordinator] Pheromone update confirmed for iteration {iteration_id}")
                except (json.JSONDecodeError, KeyError):
                    print("[Coordinator] Warning: Received iteration_updated but couldn't parse iteration_id")
            else:
                print("[Coordinator] Warning: No iteration_updated acknowledgment received")
            
            # Query best solution from pheromone manager
            msg = Message(to=self.agent.pheromone_manager_jid)
            msg.set_metadata("performative", "get_best_solution")
            msg.body = json.dumps({
                "iteration_id": self.agent.iteration
            })
            await self.send(msg)
            
            # Manually filter for best solution response
            start_time = asyncio.get_event_loop().time()
            timeout = 2
            response = None
            
            while True:
                elapsed = asyncio.get_event_loop().time() - start_time
                remaining = timeout - elapsed
                if remaining <= 0:
                    break
                
                msg = await self.receive(timeout=min(remaining, 0.1))
                if msg and msg.get_metadata("performative") == "best_solution_response":
                    response = msg
                    break
            
            if response:
                try:
                    data = json.loads(response.body)
                    num_visited = data.get("best_count", 0)
                    self.agent.best_solution = data
                    print(f"[Coordinator] Best solution: {num_visited} markets visited")
                except (json.JSONDecodeError, KeyError):
                    print("[Coordinator] Warning: Could not parse best solution response")
            
            if self.agent.iteration >= self.agent.num_iterations:
                print("\n=== ACO Complete ===")
                print("Max iterations reached - stopping ACO")
                await self.agent.stop()

