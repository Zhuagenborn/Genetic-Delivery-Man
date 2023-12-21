from collections.abc import Sequence


class City:
    def __init__(self, id: int, x: float, y: float) -> None:
        self.id: int = id

        # The position.
        self.x: float = x
        self.y: float = y

    def distance(self, city: 'City') -> float:
        """
        Calculate the distance between two cities.
        :param city: Another city.
        :return: The distance.
        """
        x_dist = abs(self.x - city.x)
        y_dist = abs(self.y - city.y)
        return (x_dist ** 2 + y_dist ** 2) ** 0.5

    def __str__(self) -> str:
        return f"{self.id}"

    def __repr__(self) -> str:
        return str(self)


class Map:
    """
    Store cities' distance and information.
    """
    def __init__(self, cities: Sequence[City]) -> None:
        assert len(cities) > 0
        self.cities: Sequence[City] = cities

        # Map each city's ID to its array index.
        self._idx: map[int, int] = {cities[i].id: i for i in range(len(cities))}

        self._dists: list[list[float]] = [[0 for _ in range(len(cities))] for _ in range(len(cities))]
        for i in range(len(cities)):
            for j in range(i + 1, len(cities)):
                dist = cities[i].distance(cities[j])
                self._dists[i][j] = dist
                self._dists[j][i] = dist

    def distance(self, id1: int, id2: int) -> float:
        """
        Get the distance between two cities.
        :param id1: A city.
        :param id2: Another city.
        :return: The distance.
        """
        idx1, idx2 = self._idx[id1], self._idx[id2]
        return self._dists[idx1][idx2]

    def city(self, id: int) -> City:
        """
        Get a city's information.
        :param id: A city's ID.
        :return: The city's information.
        """
        return self.cities[self._idx[id]]
