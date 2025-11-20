from typing import Optional

from pydantic import BaseModel, Field


# =====================================================================
# NAVIGATION REST SERVICE MODELS
# =====================================================================
class TakeoffRequest(BaseModel):
    altitude: float = Field(..., gt=0, description="Takeoff altitude in meters")


class LandRequest(BaseModel):
    pass


class MoveRequest(BaseModel):
    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")
    z: float = Field(..., description="Z coordinate in meters")


class VelocityRequest(BaseModel):
    vx: float = Field(..., description="X velocity in m/s")
    vy: float = Field(..., description="Y velocity in m/s")


class AltitudeRequest(BaseModel):
    altitude: float = Field(..., gt=0, description="Target altitude in meters")
