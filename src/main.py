import logging
import sys
import json
from pathlib import Path

import pandas as pd
from pygame.locals import *

from delivery import *
from genetic import *
from displayer import *


def load_config(path: Path) -> dict:
    """
    Load the configuration.
    """
    with path.open(encoding="utf-8") as file:
        cfg = json.load(file)
    if cfg["speed"] <= 0:
        raise ValueError("The speed must be greater than 0")
    if cfg["fps"] < 0:
        raise ValueError("The Negative FPS is not allowed")
    if cfg["mapSize"]["width"] <= 0 or cfg["mapSize"]["height"] <= 0:
        raise ValueError("The width and height of map must be greater than 0")
    if cfg["populationSize"] <= 0:
        raise ValueError("The population size must be greater than 0")
    if cfg["maxIter"]["total"] <= 0:
        raise ValueError("The maximum iteration count must be greater than 0")

    cfg["rate"]["cross"] = min(1, max(0, cfg["rate"]["cross"]))
    cfg["rate"]["mutate"] = min(1, max(0, cfg["rate"]["mutate"]))
    cfg["maxIter"]["unchanged"] = max(0, cfg["maxIter"]["unchanged"])
    return cfg


def load_orders(cities: set[int]) -> OrderList:
    """
    Load delivery orders.
    """
    data_dir = Path(__file__).parent.parent.joinpath("data")
    df = pd.read_csv(data_dir.joinpath("orders.csv")).set_index("ID")
    if df.index.duplicated(keep=False).any():
        raise ValueError(f"Duplicate orders exist")
    orders = []
    ids = set()

    def _append(order: pd.Series) -> None:
        if order.name in ids:
            raise ValueError(f"Order {{{order.name}}} is a duplicate")
        ids.add(order.name)

        city = order["City"]
        if city not in cities:
            raise ValueError(f"City {{{city}}} is invalid")
        wait_time, time_limit = order["WaitTime"], order["TimeLimit"]
        if wait_time < 0 or time_limit < 0:
            raise ValueError("The negative time is not allowed")

        orders.append(Order(order.name, city, wait_time, time_limit))

    df.apply(_append, axis="columns")
    return OrderList(orders)


def load_cities(width: int, height: int) -> tuple[list[City], set[int]]:
    """
    Load cities.
    """
    data_dir = Path(__file__).parent.parent.joinpath("data")
    df = pd.read_csv(data_dir.joinpath("cities.csv")).set_index("ID")
    if df.index.duplicated(keep=False).any():
        raise ValueError(f"Duplicate cities exist")
    cities = []

    def _append(city: pd.Series) -> None:
        x = min(width, max(0, city["X"]))
        y = min(height, max(0, city["Y"]))
        if x != city["X"] or y != city["Y"]:
            print(f"Warning: City {{{city.name}}} has been relocated from ({city['X']}, {city['Y']}) to ({x}, {y})")

        cities.append(City(city.name, x, y))

    df.apply(_append, axis="columns")
    return cities, set(df.index)


def main():
    cfg = load_config(Path(__file__).parent.joinpath("config.json"))

    # Load cities and delivery orders.
    width, height = cfg["mapSize"]["width"], cfg["mapSize"]["height"]
    cities, city_ids = load_cities(width, height)
    orders = load_orders(city_ids)
    Route.map = Map(cities)
    Route.time_on_way = TimeOnWay(Route.map, cfg["speed"])
    Route.origin = cities[0]

    # Create a population.
    population = Population()
    population.generate(cfg["populationSize"], lambda: Item(orders.random_route()))
    genetic = Genetic(population, cfg["rate"]["cross"], cfg["rate"]["mutate"], cfg["elitism"])

    # Create a genetic model.
    generation = genetic.evolve(cfg["maxIter"]["total"], cfg["maxIter"]["unchanged"])

    pygame.init()
    pygame.display.set_caption("Genetic Delivery Man")
    display = Displayer(Route.map, width, height, cfg["fps"], cfg["showCityID"])

    end = False
    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                pygame.quit()
                sys.exit()
        if not end:
            try:
                next(generation)
                display.update(genetic.best.route)
            except StopIteration:
                end = True
                route = genetic.best.route
                print(f"The shortest delay: {round(route.delay, 2)}")
                print(f"\t{route}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.DEBUG)
    logger = logging.getLogger(__name__)

    try:
        main()
    except SystemExit:
        pass
    except BaseException as err:
        logger.exception(err)
        sys.exit(1)
