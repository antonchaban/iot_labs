import asyncio
from logging import Logger
from datasource import Datasource
from kivy.app import App
from kivy_garden.mapview import MapMarker, MapView
from kivy.clock import Clock
from lineMapLayer import LineMapLayer


class MapViewApp(App):
    def __init__(self, **kwargs):
        super().__init__()
        # додати необхідні змінні

    def on_start(self):
        """
        Встановлює необхідні маркери, викликає функцію для оновлення мапи
        """
        self.datasource = Datasource(1)
        Clock.schedule_interval(self.update, 1)

    def update(self, *args):
        """
        Викликається регулярно для оновлення мапи
        """
        # Logger.debug("Get new points")
        points = self.datasource.get_new_points()
        if len(points) == 0:
            return
        for point in points:
            print(point)
            self.map_layer.add_point(point)
        self.update_car_marker(points[-1])

    def update_car_marker(self, point):
        """
        Оновлює відображення маркера машини на мапі
        :param point: GPS координати
        """
        self.map_view.remove_marker(self.car_marker)
        self.car_marker.lat = point[0]
        self.car_marker.lon = point[1]
        self.map_view.add_marker(self.car_marker)

    def set_pothole_marker(self, point):
        """
        Встановлює маркер для ями
        :param point: GPS координати
        """

    def set_bump_marker(self, point):
        """
        Встановлює маркер для лежачого поліцейського
        :param point: GPS координати
        """

    def build(self):
        """
        Ініціалізує мапу MapView(zoom, lat, lon)
        :return: мапу
        """
        self.map_layer = LineMapLayer()
        self.map_view = MapView(
            zoom=15,
            lat=50.4501,
            lon=30.5234,
        )
        self.map_view.add_layer(self.map_layer, mode="scatter")
        self.car_marker = MapMarker(
            lat=50.45034509664691,
            lon=30.5246114730835,
            source="images/car.png",
        )
        self.map_view.add_marker(self.car_marker)
        return self.map_view


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(MapViewApp().async_run(async_lib="asyncio"))
    loop.close()
