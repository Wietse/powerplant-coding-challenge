import logging
from operator import attrgetter
from dataclasses import dataclass, InitVar
import math


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


fuel_key = {
    'gasfired': 'gas(euro/MWh)',
    'turbojet': 'kerosine(euro/MWh)',
    'co2': 'co2(euro/ton)',
    'windturbine': 'wind(%)',
}


@dataclass
class Plant:
    name: str
    type: str
    efficiency: float = 1.0
    pmin: float = 0.0
    pmax: float = 0.0
    cost: float = 0.0
    fuels: InitVar = None

    def __post_init__(self, fuels):
        # calculate the cost
        # adjust pmax for wind availability
        factor = fuels[fuel_key[self.type]]
        if self.type == 'windturbine':
            self.cost = 0
            fraction = factor / 100.0
            self.pmax = round(self.pmax * fraction, 1)
        else:
            if self.efficiency > 0:
                self.cost = factor / self.efficiency
            else:
                # TODO: efficieny <= 0 is an error in the input?
                # simply exclude this plant for now
                self.pmin = 0.0
                self.pmax = 0.0
                self.cost = 10**10


def allocate_load(load, load_plan, powerplants, merit_order):
    remaining = load
    for i, plant_id in enumerate(merit_order):
        plant = powerplants[plant_id]
        quote = 0.0
        if plant.pmin <= remaining:
            quote = min(remaining, plant.pmax)
        else:
            # redistribute: we try to take the least load from a less expensive plant to fulfill pmin
            required_load = plant.pmin - remaining
            j = i
            while j > 0:
                j -=1
                id_ = merit_order[j]
                prev_plant = powerplants[id_]
                prev_allocation = load_plan[id_]
                if prev_allocation - required_load > prev_plant.pmin:
                    load_plan[id_] -= required_load
                    remaining += required_load
                    quote = plant.pmin
                    break
        load_plan[plant_id] += quote
        remaining -= quote
        if not remaining:
            break
    return load - remaining


def prepare_input(config):
    fuels = config['fuels']
    plants = {d['name']: Plant(**d, fuels=fuels) for d in config['powerplants']}
    merit_order = [p.name for p in sorted(plants.values(), key=attrgetter('cost'))]
    return config['load'], plants, merit_order


def distribute_load(config):
    """
    Example return value:
    [
        { 'name': 'windpark1', 'p': 75 },
        { 'name': 'windpark2', 'p': 18 },
        { 'name': 'gasfiredbig1', 'p': 200 },
        { 'name': 'gasfiredbig1', 'p': 0 },
        { 'name': 'tj1', 'p': 0 },
        { 'name': 'tj2', 'p': 0 }
    ]
    """
    load, plants, merit_order = prepare_input(config)
    logger.debug('distribute_load: load=%s\nmerit_order=%s', load, merit_order)
    load_plan = {name: 0.0 for name in plants}
    allocated = allocate_load(load, load_plan, plants, merit_order)
    if not math.isclose(allocated, load):
        raise Exception('Unable to distribute load: load=%s, allocated=%s' % (load, allocated))
    return [{'name': name, 'p': p} for name, p in load_plan.items()]
