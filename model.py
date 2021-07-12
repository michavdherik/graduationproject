"""

Use this file to write the agent-based model.

"""

from mesa import Agent, Model
from mesa.time import RandomActivation
from mesa_geo import GeoSpace
from mesa_geo.geoagent import GeoAgent, AgentCreator
from shapely.geometry import Point


# class KeniaSpace(GeoSpace):  # inherits from geospace
# def __init__(self):
#    super().__init__(self)  # inherit all methods from parent
# self.torus = False  # map is not a torus
# self._agent_points = None
# self._agent_to_index: {}

# def move_agent(self, agent, pos) -> None:
#     """Move an agent from its current position to a new position.
#     Args:
#         agent: The agent object to move.
#         pos: Coordinate tuple to move the agent to.
#     """
#     pos = self.torus_adj(pos)
#     idx = self._agent_to_index[self.agent]
#     self._agent_points[idx, 0] = pos[0]
#     self._agent_points[idx, 1] = pos[1]
#     agent.pos = pos

# def torus_adj(self, pos: Coordinate) -> Coordinate:
#     """Convert coordinate, handling torus looping."""
#     if not self.out_of_bounds(pos):
#         return pos
#     elif not self.torus:
#         raise Exception("Point out of bounds, and space non-toroidal.")
#     else:
#         return pos[0] % self.width, pos[1] % self.height


class Animal(GeoAgent):
    """Agent Class representing an animal."""

    def __init__(self, unique_id, model, shape, animal_count=1.0):
        """Create new animal agent.

        Args:
            animal_count: Animal count per viewing, as presented in gdf.
        """
        super().__init__(unique_id, model, shape)
        self.animal_count = animal_count

    def step(self):
        """Move agents. For now: do nothing."""
        pass


class AnimalModel(Model):
    """Model Class for an animal population model."""

    # Global vars
    MAP_COORDS = [1.1503504594373148, 37.213466839155515]  # Samburu Region

    def __init__(self, gdf, name):
        """Create a new animal model.
        :param gdf: GeoDataframe holding data.
        :param name: 2-letter abbreviation name for animal species to be modelled.
        """

        self.gdf = gdf
        self.name = name

        self.grid = GeoSpace(crs=gdf.crs)
        self.schedule = RandomActivation(self)

        self.steps = 0
        self.running = True

        gdf_new = gdf.filter(['geometry', name], axis=1)

        AC = AgentCreator(agent_class=GeoAgent,
                          agent_kwargs={"model": self}, crs=gdf.crs)
        animal_agents = AC.from_GeoDataFrame(gdf=gdf_new,
                                             unique_id="index", set_attributes=True)

        for animal in animal_agents:
            # Set animal count in agent
            animal.animal_count = int(getattr(animal, name))
            self.grid.add_agents(animal)
            self.schedule.add(animal)

    def step(self):
        """"Step through the model."""
        self.steps += 1

        self.reset_counts()
        self.schedule.step()
        self.grid._recreate_rtree()  # Recalculate spatial tree, because agents are moving

        if condition:
            self.running = False
