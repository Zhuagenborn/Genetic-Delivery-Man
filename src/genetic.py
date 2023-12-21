from collections.abc import Iterator, Callable, Sequence
from copy import copy

import numpy as np

from delivery import Route
from delivery import Order


class Item:
    """
    An individual in a population.
    """
    def __init__(self, route: Route) -> None:
        def calc_fitness() -> float:
            assert route.delay >= 0
            return 1 / (route.delay + 1)

        self.route: Route = route
        self.fitness = calc_fitness()

    @property
    def dna(self) -> Sequence[Order]:
        """
        Get the DNA, which is the delivery sequence.
        """
        return self.route.orders


ItemCreator = Callable[[], Item]


class Population:
    """
    A population containing various individuals.
    """
    def __init__(self) -> None:
        self.items: list[Item] = None

    def generate(self, size: int, creator: ItemCreator) -> None:
        """
        Randomly generate a number of individuals.
        :param size: The size of the population.
        :param creator: A method used to create an individual.
        """
        assert size > 0
        self.items = [creator() for _ in range(size)]

    def __getitem__(self, idx: int) -> Item:
        return self.items[idx]

    def __setitem__(self, idx: int, item: Item) -> None:
        self.items[idx] = item

    @property
    def best(self) -> tuple[int, Item]:
        """
        Get the best individual and its index.
        """
        idx = np.argmax(self.fitness)
        return idx, self.items[idx]

    @property
    def worst(self) -> tuple[int, Item]:
        """
        Get the worst individual and its index.
        """
        idx = np.argmin(self.fitness)
        return idx, self.items[idx]

    @property
    def fitness(self) -> list[float]:
        """
        Get all individuals' fitness.
        """
        return [item.fitness if item is not None else 0 for item in self.items]

    @property
    def size(self) -> int:
        """
        Get the size of the population.
        """
        return len(self.items)

    def __copy__(self) -> 'Population':
        new_ins = Population()
        new_ins.items = self.items.copy()
        return new_ins


class Genetic:
    """
    A genetic model.
    """
    def __init__(self, population: Population, cross_rate: float, mutate_rate: float, elitism: bool) -> None:
        self.best: Item = population.best[1]
        self.population: Population = population
        self.cross_rate: float = cross_rate
        self.mutate_rate: float = mutate_rate
        self._elitism: bool = elitism

    def evolve(self, max_iter: int, max_unchanged_iter: int = 0) -> Iterator[tuple[int, Item]]:
        """
        Population evolves.
        :param max_iter: The maximum iteration number before stopping evolution.
        :param max_unchanged_iter:
        The maximum iteration number that the best individual remains unchanged.
        If it is less than 1, the model will not consider it.
        :return: The current iteration number and the best individual from the current population.
        """
        assert max_iter > 0 and max_unchanged_iter >= 0
        curr_unchanged_iter = 0

        def update_best(iter: int, item: Item) -> None:
            nonlocal curr_unchanged_iter
            if self.best.fitness < item.fitness:
                print(f"({iter + 1}) Update the shortest delay: {round(self.best.route.delay, 2)} -> {round(item.route.delay, 2)}")
                print(f"\t{item.route}")
                self.best = item
                curr_unchanged_iter = 0
            else:
                curr_unchanged_iter += 1

        for i in range(max_iter):
            curr_best = self._evolve()
            update_best(i, curr_best)
            yield i, curr_best
            if 0 < max_unchanged_iter <= curr_unchanged_iter:
                break

    def _select(self) -> None:
        """
        Select the next generation.
        """
        fitness = np.array(self.population.fitness)
        self.population.items = list(np.random.choice(
            self.population.items, size=self.population.size, replace=True, p=fitness / fitness.sum()))

    def _mutate(self, item: Item) -> Item:
        """
        Mutation.
        """
        new_dna = list(item.dna)
        for i in range(len(item.dna)):
            if np.random.rand() < self.mutate_rate:
                # Swap two genes.
                j = np.random.randint(0, len(item.dna))
                new_dna[i], new_dna[j] = new_dna[j], new_dna[i]
        return Item(Route(new_dna))

    def _crossover(self, item: Item, population: Population) -> Item:
        """
        Ordered crossover.
        """
        if np.random.rand() < self.cross_rate:
            # Pick another parent.
            parent = population.items[np.random.randint(0, population.size)]

            # Randomly select a subsequence of the first parent's DNA.
            idx1, idx2 = np.random.randint(0, len(item.dna)), np.random.randint(0, len(item.dna))
            begin, end = min(idx1, idx2), max(idx1, idx2)

            dna1 = []
            for i in range(begin, end):
                dna1.append(item.dna[i])
            # Then fill the remainder with DNA from the second parent in the order in which they appear, without duplicate.
            dna2 = [gene for gene in parent.dna if gene not in dna1]
            return Item(Route(dna1 + dna2))
        else:
            return item

    def _evolve(self) -> Item:
        prev_best = self.population.best[1] if self._elitism else None

        self._select()
        copied_pop = copy(self.population)
        for i in range(self.population.size):
            child = self._crossover(self.population.items[i], copied_pop)
            self.population.items[i] = self._mutate(child)

        # Elitism: Keep the best individual from the previous generation.
        if prev_best:
            curr_best = self.population.best[1]
            if curr_best.fitness < prev_best.fitness:
                worst_idx = self.population.worst[0]
                self.population[worst_idx] = prev_best

        return self.population.best[1]
