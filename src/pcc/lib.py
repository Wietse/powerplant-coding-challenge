import logging
from operator import attrgetter
from dataclasses import dataclass, InitVar

# from .naive import distribute_load
from .simplex import distribute_load


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)
