import asyncio
import json
from spade.agent import Agent
from spade.behaviour import PeriodicBehaviour
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
    
    async def setup(self):
        print(f"[Coordinator] Starting ACO algorithm")
        self.add_behaviour(self.CoordinationBehavior(period=5))
    
    class CoordinationBehavior(PeriodicBehaviour):
        
        async def run(self):
            self.agent.iteration += 1
            
            print(f"\n=== ACO Iteration {self.agent.iteration} ===")
            
            # Signal all ants to start new iteration
            for ant_jid in self.agent.ant_jids:
                msg = Message(to=ant_jid)
                msg.set_metadata("performative", "start_iteration")
                msg.body = "{}"
                await self.send(msg)
            
            # Wait for ants to finish their tours
            await asyncio.sleep(3)
            
            # Signal pheromone manager to update pheromones
            msg = Message(to=self.agent.pheromone_manager_jid)
            msg.set_metadata("performative", "end_iteration")
            msg.body = "{}"
            await self.send(msg)
            
            # Wait for pheromone update
            await asyncio.sleep(0.5)
            
            # Query best solution from pheromone manager
            msg = Message(to=self.agent.pheromone_manager_jid)
            msg.set_metadata("performative", "get_best_solution")
            msg.body = "{}"
            
            await self.send(msg)
            
            response = await self.receive(timeout=1)
            if response and response.get_metadata("performative") == "best_solution_response":
                data = json.loads(response.body)
                num_visited = data.get("best_count", 0)
                self.agent.best_solution = data
            
            if self.agent.iteration >= self.agent.num_iterations:
                print("\n=== ACO Complete ===")
                print("Max iterations reached - stopping ACO")
                await self.agent.stop()

