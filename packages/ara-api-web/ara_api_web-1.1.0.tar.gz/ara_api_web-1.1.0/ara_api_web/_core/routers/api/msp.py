from fastapi import APIRouter, Depends

from ara_api_web._core.models import (
    AltitudeResponse,
    AttitudeResponse,
    BatteryResponse,
    IMUResponse,
    MotorResponse,
    OpticalFlowResponse,
    PositionResponse,
    SonarResponse,
    VelocityResponse,
)
from ara_api_web._utils import (
    get_grpc_client,
    get_logger,
    handle_grpc_errors,
)

router: APIRouter = APIRouter(prefix="/api/msp", tags=["MSP"])


@router.get("/imu", response_model=IMUResponse)
@handle_grpc_errors
async def get_imu(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> IMUResponse:
    imu_data = grpc_client.msp_get_raw_imu()

    if imu_data is None:
        return IMUResponse(error="Failed to retrieve IMU data")

    return IMUResponse(
        gyro_x=imu_data.gyro.x,
        gyro_y=imu_data.gyro.y,
        gyro_z=imu_data.gyro.z,
        acc_x=imu_data.acc.x,
        acc_y=imu_data.acc.y,
        acc_z=imu_data.acc.z,
    )


@router.get("/altitude", response_model=AltitudeResponse)
@handle_grpc_errors
async def get_altitude(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> AltitudeResponse:
    altitude_data = grpc_client.msp_get_altitude()

    if altitude_data is None:
        return AltitudeResponse(error="Failed to retrieve altitude")

    return AltitudeResponse(altitude=altitude_data.data)


@router.get("/position", response_model=PositionResponse)
@handle_grpc_errors
async def get_position(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> PositionResponse:
    position_data = grpc_client.msp_get_position()

    if position_data is None:
        return PositionResponse(error="Failed to retrieve position")

    return PositionResponse(
        x=position_data.data.x,
        y=position_data.data.y,
        z=position_data.data.z,
    )


@router.get("/attitude", response_model=AttitudeResponse)
@handle_grpc_errors
async def get_attitude(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> AttitudeResponse:
    attitude_data = grpc_client.msp_get_attitude()

    if attitude_data is None:
        return AttitudeResponse(error="Failed to retrieve attitude")

    return AttitudeResponse(
        roll=attitude_data.data.x,
        pitch=attitude_data.data.y,
        yaw=attitude_data.data.z,
    )


@router.get("/analog", response_model=BatteryResponse)
@handle_grpc_errors
async def get_analog(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> BatteryResponse:
    analog_data = grpc_client.msp_get_analog()

    if analog_data is None:
        return BatteryResponse(error="Failed to retrieve analog data")

    return BatteryResponse(
        voltage=analog_data.voltage,
        cell_count=None,
        capacity=analog_data.mAhdrawn,
    )


@router.get("/motor", response_model=MotorResponse)
@handle_grpc_errors
async def get_motor(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> MotorResponse:
    motor_data = grpc_client.msp_get_motor()

    if motor_data is None:
        return MotorResponse(error="Failed to retrieve motor data")

    return MotorResponse(data=motor_data.data)


@router.get("/optical_flow", response_model=OpticalFlowResponse)
@handle_grpc_errors
async def get_optical_flow(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> OpticalFlowResponse:
    flow_data = grpc_client.msp_get_optical_flow()

    if flow_data is None:
        return OpticalFlowResponse(error="Failed to retrieve optical flow")

    return OpticalFlowResponse(
        quitity=flow_data.quality,
        flow_rate_x=flow_data.flow_rate.x,
        flow_rate_y=flow_data.flow_rate.y,
        body_rate_x=flow_data.body_rate.x,
        body_rate_y=flow_data.body_rate.y,
    )


@router.get("/sonar", response_model=SonarResponse)
@handle_grpc_errors
async def get_sonar(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> SonarResponse:
    sonar_data = grpc_client.msp_get_sonar()

    if sonar_data is None:
        return SonarResponse(error="Failed to retrieve sonar data")

    return SonarResponse(data=sonar_data.data)


@router.get("/velocity", response_model=VelocityResponse)
@handle_grpc_errors
async def get_velocity(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> VelocityResponse:
    position_data = grpc_client.msp_get_position()

    if position_data is None:
        return VelocityResponse(error="Failed to retrieve velocity")

    return VelocityResponse(
        x=position_data.data.x,
        y=position_data.data.x,
        z=position_data.data.x,
    )
