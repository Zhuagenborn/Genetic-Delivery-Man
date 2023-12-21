from collections.abc import Sequence
from random import shuffle

from location import Map, City


class Order:
    """
    A delivery order.
    """
    def __init__(self, id: int, city: int, wait_time: float, time_limit: float) -> None:
        assert wait_time >= 0
        assert time_limit >= 0
        self.id: int = id
        self.city: int = city   # The destination.

        # The time the customer has been waiting.
        self.wait_time: float = wait_time
        # The time limit on delivery.
        # If the time needed is greater than the limit, the exceeded is treated as a delay.
        self.time_limit: float = time_limit


class OrderList:
    """
    Order management.
    """
    def __init__(self, orders: Sequence[Order]) -> None:
        self._orders: map[int, Order] = {order.id: order for order in orders}

    def __getitem__(self, id: int) -> Order:
        """
        Get an order's information.
        :param id: An order's ID.
        :return: The order's information.
        """
        return self._orders[id]

    def random_route(self) -> 'Route':
        """
        Randomly generate a route containing all orders.
        :return: A route.
        """
        orders = list(self._orders.values())
        shuffle(orders)
        return Route(orders)


class TimeOnWay:
    """
    Store the time needed from one city to another.
    """
    def __init__(self, map: Map, speed: float) -> None:
        assert speed > 0
        self.map: Map = map
        self.speed: float = speed

        self._times: list[list[float]] = [[-1 for _ in range(len(self.map.cities))] for _ in range(len(self.map.cities))]

        # Map each city's ID to its array index.
        self._city_idx: map[int, int] = {self.map.cities[i].id: i for i in range(len(self.map.cities))}

    def __getitem__(self, ids: tuple[int, int]) -> float:
        """
        Get the time needed between two cities.
        :param ids: Two cities' IDs.
        :return: The time.
        """
        id1, id2 = ids
        idx1, idx2 = self._city_idx[id1], self._city_idx[id2]
        if self._times[idx1][idx2] < 0:
            time = self.map.distance(id1, id2) / self.speed
            self._times[idx1][idx2] = time
            self._times[idx2][idx1] = time
        return self._times[idx1][idx2]


class Route:
    """
    A delivery route.
    """
    time_on_way: TimeOnWay = None
    map: Map = None

    # The delivery company. It's a fixed starting point.
    origin: City = None

    def __init__(self, orders: Sequence[Order]) -> None:
        assert len(orders) > 0
        self.orders: Sequence[Order] = orders

        self._delay: float = -1

    @property
    def delay(self) -> float:
        """
        Get the delay time.
        """
        if self._delay < 0:
            def calc_delay(needed: float, limit: float) -> float:
                return max(0, needed - limit)

            # Calculate the time from the origin to the first city.
            total_needed = self.time_on_way[self.origin.id, self.orders[0].city]
            total_delay = calc_delay(total_needed + self.orders[0].wait_time, self.orders[0].time_limit)

            # Calculate the time between the other cities.
            for i in range(1, len(self.orders)):
                total_needed += self.time_on_way[self.orders[i - 1].city, self.orders[i].city]
                total_delay += calc_delay(total_needed + self.orders[i].wait_time, self.orders[i].time_limit)
            self._delay = total_delay
        return self._delay

    def __str__(self) -> str:
        str_repr = f"{str(self.origin)} -> "
        for i in range(0, len(self.orders) - 1):
            str_repr += f"{str(self.map.city(self.orders[i].city))} -> "
        return str_repr + f"{str(self.map.city(self.orders[-1].city))}"

    def __repr__(self) -> str:
        return str(self)
