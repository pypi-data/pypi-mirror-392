from pydantic import BaseModel


class CorrelatedDetection(BaseModel):
    satellite_id: str
    right_ascension: float
    declination: float
    magnitude: float
    angle_between_centroids: float
    cross_line_of_sight_range: float
