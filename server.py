import math
from model import AnimalModel
from preprocess import get_population_data
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

    img_loc = "elephant_emoji.png"

    portrayal = dict()
    # portrayal['shape'] = img_loc
    # portrayal['scale'] = math.sqrt(agent.animal_count)
    portrayal["color"] = "Red"
    portrayal["radius"] = math.sqrt(agent.animal_count)

    return portrayal


elephants, buffalos = get_population_data()
(gdf, name) = elephants

model_params = {"gdf": gdf,
                "name": name,
                }

step_element = StepElement()
map_element = MapModule(agent_portrayal,
                        view=AnimalModel.MAP_COORDS,
                        zoom=7,
                        map_height=500, map_width=500)

server = ModularServer(AnimalModel,
                       [map_element, step_element],
                       f"{name} Model",
                       model_params)

server.port = 8521  # The default
server.launch()
