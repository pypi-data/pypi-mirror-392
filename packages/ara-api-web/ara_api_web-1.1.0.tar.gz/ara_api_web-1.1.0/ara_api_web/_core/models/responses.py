from typing import Optional

from pydantic import BaseModel


class StatusResponse(BaseModel):
    status: str
    details: Optional[str] = None


# =====================================================================
# MSP REST SERVICE MODELS
# =====================================================================
class IMUResponse(BaseModel):
    gyro_x: Optional[float] = None
    gyro_y: Optional[float] = None
    gyro_z: Optional[float] = None
    acc_x: Optional[float] = None
    acc_y: Optional[float] = None
    acc_z: Optional[float] = None
    error: Optional[str] = None


class MotorResponse(BaseModel):
    data: Optional[list] = None
    error: Optional[str] = None


class AttitudeResponse(BaseModel):
    roll: Optional[float] = None
    pitch: Optional[float] = None
    yaw: Optional[float] = None
    error: Optional[str] = None


class AltitudeResponse(BaseModel):
    altitude: Optional[float] = None
    error: Optional[str] = None


class SonarResponse(BaseModel):
    data: Optional[float] = None
    error: Optional[str] = None


class OpticalFlowResponse(BaseModel):
    quitity: Optional[int] = None
    flow_rate_x: Optional[float] = None
    flow_rate_y: Optional[float] = None
    body_rate_x: Optional[float] = None
    body_rate_y: Optional[float] = None
    error: Optional[str] = None


class PositionResponse(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    error: Optional[str] = None


class VelocityResponse(BaseModel):
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
    error: Optional[str] = None


class BatteryResponse(BaseModel):
    voltage: Optional[float] = None
    cell_count: Optional[int] = None
    capacity: Optional[int] = None
    error: Optional[str] = None


# =====================================================================
# MSP REST SERVICE MODELS
# =====================================================================
class ImageResponse(BaseModel):
    height: Optional[int] = None
    weight: Optional[int] = None
    data: Optional[bytes] = None
    noise: Optional[float] = None
    error: Optional[str] = None


class ArucoResponse(BaseModel):
    id: Optional[int] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    pos_z: Optional[float] = None
    orient_x: Optional[float] = None
    orient_y: Optional[float] = None
    orient_z: Optional[float] = None
    error: Optional[str] = None


class BlobResponse(BaseModel):
    id: Optional[int] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
    size: Optional[float] = None


class QRResponse(BaseModel):
    data: Optional[int] = None
    pos_x: Optional[float] = None
    pos_y: Optional[float] = None
