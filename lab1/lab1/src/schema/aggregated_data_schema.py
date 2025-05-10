from marshmallow import Schema, fields

from src.schema.accelerometer_schema import AccelerometerSchema
from src.schema.gps_schema import GpsSchema


class AggregatedDataSchema(Schema):
    accelerometer = fields.Nested(AccelerometerSchema)
    gps = fields.Nested(GpsSchema)
    timestamp = fields.DateTime('iso')