from csv import reader
from datetime import datetime
from src.domain.aggregated_data import AggregatedData
from src.domain.accelerometer import Accelerometer
from src.domain.gps import Gps


class FileDatasource:
    def __init__(self, accelerometer_filename: str, gps_filename: str) -> None:
        # Зберігаємо шляхи до CSV-файлів акселерометра та GPS
        self.accelerometer_filename = accelerometer_filename
        self.gps_filename = gps_filename

        # Списки для зберігання зчитаних рядків з файлів
        self.accel_data = []
        self.gps_data = []

        # Індекс, який відстежує, який рядок повертати наступним
        self.index = 0

    def startReading(self, *args, **kwargs):
        # Відкриваємо файл акселерометра та зчитуємо всі рядки
        with open(self.accelerometer_filename, 'r') as acc_file:
            self.accel_data = list(reader(acc_file))

        # Відкриваємо файл GPS та зчитуємо всі рядки
        with open(self.gps_filename, 'r') as gps_file:
            self.gps_data = list(reader(gps_file))

        # Пропускаємо перший рядок, якщо це заголовок (перевірка на нечислові значення)
        if self.accel_data and not self.accel_data[0][0].isdigit():
            self.accel_data = self.accel_data[1:]
        if self.gps_data and not self.gps_data[0][0].replace('.', '', 1).isdigit():
            self.gps_data = self.gps_data[1:]

        # Скидаємо індекс до початку
        self.index = 0

    def read(self) -> AggregatedData:
        # Перевірка: чи були зчитані дані
        if not self.accel_data or not self.gps_data:
            raise RuntimeError("Data not loaded. Call startReading() first.")

        # Циклічне зчитування — коли доходимо до кінця, повертаємося на початок
        accel_row = self.accel_data[self.index % len(self.accel_data)]
        gps_row = self.gps_data[self.index % len(self.gps_data)]
        self.index += 1

        # Створюємо об'єкти зчитаних даних
        accel = Accelerometer(
            x=int(accel_row[0]),
            y=int(accel_row[1]),
            z=int(accel_row[2])
        )

        gps = Gps(
            longitude=float(gps_row[0]),
            latitude=float(gps_row[1])
        )

        # Повертаємо об'єкт AggregatedData з поточним часом
        return AggregatedData(
            accelerometer=accel,
            gps=gps,
            timestamp=datetime.utcnow()
        )

    def stopReading(self, *args, **kwargs):
        # Очищаємо збережені дані та скидаємо індекс
        self.accel_data = []
        self.gps_data = []
        self.index = 0
