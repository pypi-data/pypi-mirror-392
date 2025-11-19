from pydantic import BaseModel, Field

DEFAULT_ANGLE_DISTANCE_CORRELATION = 0.1  # in degrees


class CorrelationSettings(BaseModel):

    centroid_angle_limit: float = Field(
        default=DEFAULT_ANGLE_DISTANCE_CORRELATION,
        description="Maximum allowed centroid angle difference for correlation in degrees",
        ge=0.0,
        le=180.0,
    )
