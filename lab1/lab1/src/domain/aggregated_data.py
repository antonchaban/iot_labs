from dataclasses import dataclass
from datetime import datetime
from src.domain.accelerometer import Accelerometer
from src.domain.gps import Gps

@dataclass
class AggregatedData:
    accelerometer: Accelerometer
    gps: Gps
    timestamp: datetime
    user_id: int