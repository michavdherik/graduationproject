import math
from matplotlib import cm
import matplotlib.colors as mc
from model import AnimalModel, Animal, NDVIcell
from preprocess import get_2017_population_data
from sentinel import get_ndvi_gdf
from mesa_geo.visualization.MapModule import MapModule
from mesa.visualization.modules import TextElement
from mesa_geo.visualization.ModularVisualization import ModularServer


class StepElement(TextElement):
    """
    Display a text count of how many steps have been taken
    """

    def __init__(self):
        pass

    def render(self, model):
        return "Steps: " + str(model.steps)


def agent_portrayal(agent):
    """Portayal function to send to visualize agent"""

    # TODO: match color with animal species
    # TODO: animal emoji image instead of dot, using scale instead of radius.
    # img_loc = "elephant_emoji.png"
    # portrayal['shape'] = img_loc
    # portrayal['scale'] = math.sqrt(agent.animal_count)

    portrayal = dict()
    if isinstance(agent, Animal):
        portrayal["color"] = "Red"
        portrayal["radius"] = math.sqrt(agent.animal_count)
        portrayal['layer'] = 1
    else:
        # Visualize NDVI-dependent color
        greens = cm.get_cmap("Greens", num_NDVI)
        # Convert NDVI value (from [-1,1] to [0,1] range)
        color_val = (float(agent.value) + 1) / 2
        portrayal['color'] = mc.to_hex(greens(color_val))
        portrayal['text'] = str(round(agent.value, 2))
        portrayal['layer'] = 0

    return portrayal


# Load animal data
elephants, buffalos = get_2017_population_data()
(gdf_animal, animal_name) = elephants
# Load NDVI data
gdf_ndvi = get_ndvi_gdf(preload=True, cloudmask=True)
num_NDVI = len(gdf_ndvi)
ndvi_value = gdf_ndvi['value']
# Get maximum NDVI value for agent portrayal
max_ndvi = gdf_ndvi['value'].max()

model_params = {"gdf_animal": gdf_animal,
                "gdf_ndvi": gdf_ndvi,
                "animal_name": animal_name,
                "ndvi_value": ndvi_value
                }

step_element = StepElement()
map_element = MapModule(agent_portrayal,
                        view=AnimalModel.MAP_COORDS,
                        zoom=7,
                        map_height=500, map_width=500)

server = ModularServer(AnimalModel,
                       [map_element, step_element],
                       f"{animal_name} Model",
                       model_params)

server.port = 8521  # The default
server.launch()
