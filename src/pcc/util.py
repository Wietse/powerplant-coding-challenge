import logging
from operator import attrgetter
from dataclasses import dataclass, InitVar


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
        if fuels is None:
            return
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
