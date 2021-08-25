"""

Use this file to write the agent-based model.

"""

import os
import geopandas as gp
from mesa import Model
from mesa.time import BaseScheduler
from mesa_geo import GeoSpace
from mesa_geo.geoagent import GeoAgent, AgentCreator
from shapely.geometry import Point

poly_path = r'./data/geometries/'


class NDVIcell(GeoAgent):
    """Agent class representing stationary NDVI cells."""

    def __init__(self, unique_id, model, shape, value=-1):
        """Create new NDVI agent.`

        :param unique_id:   Unique identifier for the agent
        :param model:       Model in which the agent runs
        :param shape:       Shape object for the agent
        :param value:       NDVI value of patch
        """
        super().__init__(unique_id, model, shape)
        # Agent parameters
        self.value = value

    def step(self):
        pass

    def __repr__(self):
        return "NDVI Patch " + str(self.unique_id) + " with Value: " + str(self.value)


class Animal(GeoAgent):
    """Agent Class representing an animal."""

    def __init__(self, unique_id, model, shape, animal_count=1.0, mobility_range=0.1, ndvi_value=-1):
        """Create new animal agent.

        :param unique_id:      Unique identifier for the agent
        :param model:          Model in which the agent runs
        :param shape:          Shape object for the agent
        :param animal_count:   Animal count per viewing, as presented in gdf.
        :param mobility range: Range of distance to move in one step.
        :param ndvi:           Tuple holding underlying NDVI patch centroid and value
        """
        super().__init__(unique_id, model, shape)
        # Agent parameters
        self.animal_count = animal_count
        self.mobility_range = mobility_range  # distance travelled per step
        self.ndvi_value = ndvi_value

    def move_animal(self, destination):
        """Move animal based on surrounding NDVI values.
        :param destination: NDVI destination patch

        Return Shapely Point geometry of new position of agent.
        """

        # If destination value is more than own ndvi value,
        # calculate direction vector to destination patch
        x_dir = destination.shape.centroid.x - self.shape.x
        y_dir = destination.shape.centroid.y - self.shape.y

        step = tuple(self.mobility_range * dim for dim in [x_dir, y_dir])

        # Check if Point is within area boundaries
        if Point(self.shape.x + step[0], self.shape.y + step[1]).within(self.model.SURVEY_POLYGON):
            return Point(self.shape.x + step[0],
                         self.shape.y + step[1])
        else:
            # If new location not within area, don't move
            return Point(self.shape.x,
                         self.shape.y)

    def step(self):
        """Advance one step."""

        # Calculate NDVI patch with maximum value
        all_ndvi = [agent for agent in self.model.grid.agents
                    if isinstance(agent, NDVIcell)]
        ndvi_max = max(all_ndvi, key=lambda x: x.value)

        # Move to patch with maximum NDVI
        if ndvi_max.value > self.ndvi_value:
            self.shape = self.move_animal(ndvi_max)

    def __repr__(self):
        return "Observation: " + str(self.unique_id)


class AnimalModel(Model):
    """Model Class for an animal population model."""

    # Global vars
    MAP_COORDS = [1.1503504594373148, 37.213466839155515]  # Samburu Region
    SURVEY_POLYGON = gp.read_file(os.path.join(
        poly_path, 'Census2017Polygon-filled.shp'))['geometry'].values[0]  # Survey Area Polygon

    def __init__(self, gdf_animal, gdf_ndvi, animal_name, ndvi_value):
        """
        Create a new animal model.
        :param gdf_animal: GeoDataframe with animal data.
        :param gdf_ndvi: GeoDataframe with NDVI data.
        :param animal_name: 2-letter abbreviation name for animal species to be modelled.
        :param ndvi_value: NDVI value as present in gdf_ndvi.
        """

        # Input parameters
        self.gdf_animal = gdf_animal
        self.gdf_ndvi = gdf_ndvi
        self.animal_name = animal_name
        self.ndvi_value = ndvi_value

        # Make sure that projections are equal
        if not gdf_animal.crs == gdf_ndvi.crs:
            gdf_ndvi = gdf_ndvi.to_crs(gdf_animal.crs)
        self.grid = GeoSpace(crs=gdf_animal.crs)

        self.schedule = BaseScheduler(self)

        # Model running parameters
        self.steps = 0
        self.running = True

        # Set up the NDVI patches(add to schedule later)
        AC = AgentCreator(agent_class=NDVIcell,
                          agent_kwargs={"model": self},
                          crs=gdf_ndvi.crs)
        ndvi_agents = AC.from_GeoDataFrame(gdf=gdf_ndvi,
                                           unique_id="index",
                                           set_attributes=True)
        self.grid.add_agents(ndvi_agents)
        print("NDVI agents added to grid.")

        # Set up Animal Agents
        gdf_animal = gdf_animal.filter(['geometry', animal_name], axis=1)

        AC = AgentCreator(agent_class=Animal,
                          agent_kwargs={"model": self},
                          crs=gdf_animal.crs)
        animal_agents = AC.from_GeoDataFrame(gdf=gdf_animal,
                                             unique_id="index",
                                             set_attributes=True)
        self.grid.add_agents(animal_agents)
        print("Animal agents added to grid.")

        # Add agents to schedule
        for ndvi in ndvi_agents:
            ndvi.value = getattr(ndvi, 'value')
            self.schedule.add(ndvi)
        print("NDVI agents added to schedule.")

        for animal in animal_agents:
            # Set animal count in agent; column 'animal_name' has animal count values'
            animal.animal_count = int(getattr(animal, animal_name))
            self.schedule.add(animal)
        print("Animal agents added to schedule.")

        self.get_animal_ndvi_pairs()

    def get_animal_ndvi_pairs(self):
        """Calculate which animals are located on which NDVI patch.

        Return: Dictionary of {Animal: NDVI}"""

        observations = [agent for agent in self.grid.agents
                        if isinstance(agent, Animal)]

        for idx, observation in enumerate(observations):
            # NDVI Patches that agent is within, can only be one
            Local_NDVI = next(self.grid.get_relation(observation, "within"))
            if isinstance(Local_NDVI, NDVIcell):
                # Set observation's NDVI
                observation.ndvi = Local_NDVI.value

    def step(self):
        """"Step through the model."""

        self.steps += 1
        self.schedule.step()

        self.grid._recreate_rtree()  # Recalculate spatial tree, because agents are moving
