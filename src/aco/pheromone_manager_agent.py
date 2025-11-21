import asyncio
import json

from spade.agent import Agent
from spade.behaviour import CyclicBehaviour
from spade.template import Template


class PheromoneManagerAgent(Agent):
    """
    Central agent managing pheromone trails.
    Maintains τ matrix and processes ant queries/deposits.
    """
    
    def __init__(self, jid, password, num_locations, markets,
                 initial_pheromone=1.0, decay=0.95):
        super().__init__(jid, password)
        self.num_locations = num_locations
        self.decay_coefficient = decay
        self.markets = markets
        
        # map market ids to indices in the pheromone matrix
        # needed because market ids are not necessarily sequential in the case of several days
        self.market_to_index = {int(key): idx+1 for idx, key in enumerate(markets.keys())}
        
        self.pheromone = {}
        for i in range(1, num_locations + 1):
            self.pheromone[i] = {}
            for j in range(1, num_locations + 1):
                self.pheromone[i][j] = initial_pheromone
        
        self.best_solutions = []
        self.iteration = 0
        self.iteration_tours = []  # Collect tours from all ants in iteration
        self.global_best_tour = None
        self.global_best_count = 0
    
    async def setup(self):
        print(f"[PheromoneManager] Starting at {self.jid}")
        
        # Behavior 1: Handle pheromone queries from ants
        template = Template()
        template.set_metadata("performative", "query_pheromone")
        behav = self.PheromoneQueryBehavior()
        self.add_behaviour(behav, template)
        
        # Behavior 2: Handle pheromone deposits from ants
        deposit_template = Template()
        deposit_template.set_metadata("performative", "deposit_pheromone")
        deposit_behav = self.PheromoneDepositBehavior()
        self.add_behaviour(deposit_behav, deposit_template)
        
        # Behavior 3: Handle best solution queries from coordinator
        best_solution_template = Template()
        best_solution_template.set_metadata("performative", "get_best_solution")
        best_solution_behav = self.BestSolutionBehavior()
        self.add_behaviour(best_solution_behav, best_solution_template)
        
        # Behavior 4: Handle iteration end and update pheromones
        update_template = Template()
        update_template.set_metadata("performative", "end_iteration")
        update_behav = self.IterationUpdateBehavior()
        self.add_behaviour(update_behav, update_template)
    
    class PheromoneQueryBehavior(CyclicBehaviour):
        """Responds to pheromone level queries from ants"""
        async def run(self):
            try:
                msg = await self.receive(timeout=5)
            except asyncio.CancelledError:
                return
            if msg:
                data = json.loads(msg.body)
                from_loc = data["from"]
                to_loc = data["to"]
                
                pheromone_level = self.agent.pheromone.get(
                    from_loc, {}
                ).get(to_loc, 1.0)
                
                response = msg.make_reply()
                response.body = json.dumps({
                    "from": from_loc,
                    "to": to_loc,
                    "pheromone": pheromone_level
                })
                response.set_metadata("performative", "pheromone_response")
                
                await self.send(response)
    
    class PheromoneDepositBehavior(CyclicBehaviour):
        """Collects tour submissions from ants (no immediate update)"""
        async def run(self):
            try:
                msg = await self.receive(timeout=5)
            except asyncio.CancelledError:
                return
            if msg:
                data = json.loads(msg.body)
                tour = data["tour"]
                num_visited = len(tour)
                
                # Store tour for batch update at iteration end
                self.agent.iteration_tours.append({
                    "tour": tour,
                    "count": num_visited
                })
    
    class IterationUpdateBehavior(CyclicBehaviour):
        """Updates pheromones after all ants complete iteration"""
        async def run(self):
            try:
                msg = await self.receive(timeout=10)
            except asyncio.CancelledError:
                return
            if msg:
                self.agent.iteration += 1
                
                # Apply evaporation to all edges
                for i in self.agent.pheromone:
                    for j in self.agent.pheromone[i]:
                        self.agent.pheromone[i][j] *= self.agent.decay_coefficient
                
                # Find best tour from this iteration
                if self.agent.iteration_tours:
                    iteration_best = max(
                        self.agent.iteration_tours,
                        key=lambda x: x["count"]
                    )
                    
                    # Update global best
                    if iteration_best["count"] > self.agent.global_best_count:
                        self.agent.global_best_tour = iteration_best["tour"]
                        self.agent.global_best_count = iteration_best["count"]
                        self.agent.best_solutions.append({
                            "tour": iteration_best["tour"],
                            "count": iteration_best["count"],
                            "iteration": self.agent.iteration
                        })
                        print(f"New global best: {iteration_best['count']} markets")
                    
                    # Reinforce ONLY the global best solution (elitism)
                    if self.agent.global_best_tour:
                        reward = self.agent.global_best_count / self.agent.num_locations
                        deposit_amount = reward * 2.0  # Boost for best solution
                        
                        for idx in range(len(self.agent.global_best_tour) - 1):
                            # map market ids to indices in the pheromone matrix
                            from_loc = self.agent.market_to_index[self.agent.global_best_tour[idx]]
                            to_loc = self.agent.market_to_index[self.agent.global_best_tour[idx + 1]]
                            # update pheromone matrix
                            self.agent.pheromone[from_loc][to_loc] += deposit_amount
                
                # Clear tours for next iteration
                self.agent.iteration_tours = []
                
                # Send acknowledgment
                response = msg.make_reply()
                response.body = "{}"
                response.set_metadata("performative", "iteration_updated")
                await self.send(response)
    
    class BestSolutionBehavior(CyclicBehaviour):
        """Responds to best solution queries from coordinator"""
        async def run(self):
            try:
                msg = await self.receive(timeout=5)
            except asyncio.CancelledError:
                return
            if msg:
                response = msg.make_reply()
                if self.agent.best_solutions:
                    best = self.agent.best_solutions[-1]
                    response.body = json.dumps({
                        "best_count": best["count"],
                        "best_tour": best["tour"],
                        "iteration": best["iteration"]
                    })
                else:
                    response.body = json.dumps({
                        "best_count": self.agent.global_best_count,
                        "best_tour": self.agent.global_best_tour if self.agent.global_best_tour else [],
                        "iteration": self.agent.iteration
                    })
                response.set_metadata("performative", "best_solution_response")
                await self.send(response)
