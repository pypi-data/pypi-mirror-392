from typing import Optional

from pydantic import BaseModel, Field


class StatusResponse(BaseModel):
    status: str
    details: Optional[str] = None


# =====================================================================
# NAVIGATION REST SERVICE MODELS
# =====================================================================
class TakeoffRequest(BaseModel):
    altitude: float = Field(
        ..., gt=0, description="Takeoff altitude in meters"
    )


class LandRequest(BaseModel):
    pass


class MoveRequest(BaseModel):
    x: float = Field(..., description="X coordinate in meters")
    y: float = Field(..., description="Y coordinate in meters")
    z: float = Field(..., description="Z coordinate in meters")


class VelocityRequest(BaseModel):
    vx: float = Field(..., description="X velocity in m/s")
    y: float = Field(..., description="Y velocity in m/s")


class AltitudeRequest(BaseModel):
    altitude: float = Field(..., gt=0, description="Target altitude in meters")


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
    x: Optional[float] = None
    y: Optional[float] = None
    z: Optional[float] = None
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
