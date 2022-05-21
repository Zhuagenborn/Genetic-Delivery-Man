import pygame

from delivery import Route
from location import Map, City


class Displayer:
    _MARGIN: int = 40
    _WHITE: tuple[int, int, int] = (255, 255, 255)
    _RED: tuple[int, int, int] = (235, 30, 25)
    _BLUE: tuple[int, int, int] = (0, 160, 230)
    _BLACK: tuple[int, int, int] = (0, 0, 0)
    _GRAY: tuple[int, int, int] = (127, 127, 127)

    def __init__(self, map: Map, width: int, height: int, fps: int, show_city_id: bool) -> None:
        self._fps: int = fps
        self._map: Map = map
        self._clock: pygame.time.Clock = pygame.time.Clock()
        self._show_city_id: bool = show_city_id
        self._font: pygame.font = pygame.font.SysFont("comicsansms", 15)
        self._window: pygame.Surface = pygame.display.set_mode((width + self._MARGIN * 2, height + self._MARGIN * 2))

    def update(self, route: Route) -> None:
        self._window.fill(self._WHITE)
        self._draw_route(route)
        self._show_delay(route)
        pygame.display.update()
        self._clock.tick(self._fps)

    def _show_delay(self, route: Route) -> None:
        """
        Show a delay message.
        """
        result_surf = self._font.render(f"The delay: {round(route.delay, 2)}", True, self._BLACK)
        self._window.blit(result_surf, (self._MARGIN, self._window.get_height() - self._MARGIN))

    def _draw_route(self, route: Route) -> None:
        """
        Draw a route.
        """
        def adjust_pos(x: float, y: float) -> tuple[float, float]:
            """
            Keep the margin around the window.
            """
            return x + self._MARGIN, y + self._MARGIN

        def draw_city(city: City, color: tuple[int, int, int]) -> None:
            pygame.draw.circle(self._window, color, adjust_pos(city.x, city.y), 5, 0)
            # Show a city's ID.
            if self._show_city_id:
                id_surf = self._font.render(str(city.id), True, self._BLACK)
                self._window.blit(id_surf, adjust_pos(city.x, city.y))

        curr = route.origin
        draw_city(curr, self._BLUE)
        for i in range(len(route.orders)):
            next = self._map.city(route.orders[i].city)
            draw_city(next, self._RED)
            pygame.draw.line(self._window, self._GRAY, adjust_pos(curr.x, curr.y), adjust_pos(next.x, next.y), 2)
            curr = self._map.city(route.orders[i].city)
