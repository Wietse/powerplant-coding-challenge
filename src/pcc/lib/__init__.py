import logging
from operator import itemgetter
import math


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


# A few "shortcuts"
pname = itemgetter('name')
ptype = itemgetter('type')
peffciency = itemgetter('efficiency')
ppmin = itemgetter('pmin')
ppmax = itemgetter('pmax')
production = itemgetter('p')


fuel_key = {
    'gasfired': 'gas(euro/MWh)',
    'turbojet': 'kerosine(euro/MWh)',
    'co2': 'co2(euro/ton)',
    'windturbine': 'wind(%)',
}


def cost(powerplant, fuels):
    plant_type = ptype(powerplant)
    if plant_type == 'windturbine':
        return 0
    factor = fuels[fuel_key[plant_type]]
    efficiency = peffciency(powerplant)
    if efficiency:
        return factor / efficiency
    # TODO: efficieny == 0 is an error in the input?
    # return an arbitrary "large cost" for now.
    return 10**10


def reset_allocation(powerplants):
    for plant in powerplants.values():
        plant['p'] = 0.0


def allocate_load(load, fuels, powerplants, merit_order, fill_factor):
    allocated = 0.0
    for _, plant_id in merit_order:
        plant = powerplants[plant_id]
        current_allocated_load = plant.setdefault('p', 0)
        quote = 0.0
        if load:
            if ptype(plant) == 'windturbine':
                fraction = fuels[fuel_key['windturbine']] / 100.0
            else:
                fraction = 1
            pmin = round(ppmin(plant) * fraction - current_allocated_load, 1)  # can be < 0!
            pmax = round((ppmax(plant) * fraction - current_allocated_load) * fill_factor, 1)
            if pmin <= load:
                quote = min(load, pmax)
            else:
                quote = 0
        plant['p'] += quote
        load -= quote
        allocated += quote
    return allocated


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
    load = config['load']
    logger.debug('distribute_load: load=%s', load)
    fuels = config['fuels']
    powerplants = {pname(plant): plant for plant in config['powerplants']}
    merit_order = sorted((cost(plant, fuels), pname(plant)) for plant in powerplants.values())
    logger.debug('distribute_load: merit_order=%s', merit_order)
    total_allocated = 0.0
    for c in range(100, 0, -10):
        fill_factor = c / 100.0
        allocated = allocate_load(load, fuels, powerplants, merit_order, fill_factor)
        total_allocated = allocated
        if not math.isclose(total_allocated, load):
            allocated = allocate_load(load - total_allocated, fuels, powerplants, merit_order, 1.0)
            total_allocated += allocated
        if math.isclose(total_allocated, load):
            logger.debug('distribute_load: succeeded with fill_factor=%s', fill_factor)
            break
        else:
            reset_allocation(powerplants)
    if not math.isclose(allocated, load):
        raise Exception('Unable to distribute load')

    return [{'name': pname(plant), 'p': production(plant)} for plant in powerplants.values()]
