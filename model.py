"""

Use this file to write the agent-based model.

"""

from mesa import Model
from mesa.time import RandomActivation
from mesa_geo import GeoSpace
from mesa_geo.geoagent import GeoAgent, AgentCreator
# from mesa.datacollection import DataCollector

from shapely.geometry import Point
from preprocess import get_population_data


class Animal(GeoAgent):
    """Agent Class representing an animal."""

    def __init__(
        self,
        unique_id,
        model,
        shape,
        animal_count=1.0,
        mobility_range=0.1,
    ):
        """Create new animal agent.

        :param unique_id:      Unique identifier for the agent
        :param model:          Model in which the agent runs
        :param shape:          Shape object for the agent
        :param animal_count:   Animal count per viewing, as presented in gdf.
        :param mobility range: Range of distance to move in one step.
        """
        super().__init__(unique_id, model, shape)
        # Agent parameters
        self.animal_count = animal_count
        self.mobility_range = mobility_range  # distance travelled per step

    def move_animal(self, dx, dy):
        """
        Move an animal by creating a new one, in a new position.
        For now: random movements.
        :param dx:  Distance to move in x-axis
        :param dy:  Distance to move in y-axis
        """
        return Point(self.shape.x + dx, self.shape.y + dy)

    def step(self):
        """Advance one step."""
        move_x = self.random.uniform(-self.mobility_range,
                                     self.mobility_range)
        move_y = self.random.uniform(-self.mobility_range,
                                     self.mobility_range)
        self.shape = self.move_animal(move_x, move_y)  # Reassign shape

    def __repr__(self):
        return "Animal: " + str(self.unique_id)


class AnimalModel(Model):
    """Model Class for an animal population model."""

    # Global vars
    MAP_COORDS = [1.1503504594373148, 37.213466839155515]  # Samburu Region

    def __init__(self, gdf, name):
        """
        Create a new animal model.
        :param gdf: GeoDataframe holding data.
        :param name: 2-letter abbreviation name for animal species to be modelled.
        """

        # Input parameters
        self.gdf = gdf
        self.name = name

        # Model parameters
        self.grid = GeoSpace(crs=gdf.crs)
        self.schedule = RandomActivation(self)

        # Model running parameters
        self.steps = 0
        self.running = True
        # self.datacollector = DataCollector(
        #     agent_reporters={"Location"=agent.shape.coords}
        # )

        gdf_new = gdf.filter(['geometry', name], axis=1)

        AC = AgentCreator(agent_class=Animal,
                          agent_kwargs={"model": self}, crs=gdf.crs)
        animal_agents = AC.from_GeoDataFrame(gdf=gdf_new,
                                             unique_id="index", set_attributes=True)
        # self.grid.add_agents(animal_agents)

        for animal in animal_agents:
            # Set animal count in agent
            animal.animal_count = int(getattr(animal, name))
            self.schedule.add(animal)
            self.grid.add_agents(animal)

    def step(self):
        """"Step through the model."""

        self.steps += 1
        self.schedule.step()
        # self.datacollector.collect(self)
        self.grid._recreate_rtree()  # Recalculate spatial tree, because agents are moving

        # # TODO: implement condition so stop running (if condition self.running = False)


# elephants, buffalos = get_population_data()
# (gdf, name) = elephants
# model = AnimalModel(gdf=gdf, name=name)
# for i in range(10):
#     print("Step:", i)
#     model.step()
