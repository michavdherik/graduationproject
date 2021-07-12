import math
from model import AnimalModel
from preprocess import get_population_data
from mesa_geo.visualization.MapModule import MapModule
from mesa_geo.visualization.ModularVisualization import ModularServer

img_loc = r"elephant_emoji.png"


def agent_portrayal(agent):
    """Portayal function to send to visualize agent"""

    portrayal = dict()
    portrayal["shape"] = img_loc
    print(type(portrayal['shape']))
    portrayal["scale"] = math.sqrt(agent.animal_count)
    # portrayal["color"] = "Red"  # TODO: match color with animal species

    return portrayal


elephants, buffalos = get_population_data()
(gdf, name) = elephants

model_params = {"gdf": gdf,
                "name": name,
                }

map_element = MapModule(agent_portrayal,
                        view=AnimalModel.MAP_COORDS,
                        zoom=7,
                        map_height=500, map_width=500)
server = ModularServer(AnimalModel,
                       [map_element],
                       f"{name} Model",
                       model_params)
server.port = 8521  # The default
server.launch()
