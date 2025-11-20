from fastapi import APIRouter, Depends

from ara_api_web._core.models import (
    LandRequest,
    MoveRequest,
    StatusResponse,
    TakeoffRequest,
    VelocityRequest,
)
from ara_api_web._utils import (
    altitude_data,
    get_grpc_client,
    get_logger,
    get_request,
    handle_grpc_errors,
    vector2,
    vector3,
)

router: APIRouter = APIRouter(prefix="/api/navigation", tags=["Navigation"])


@router.post("/takeoff", response_model=StatusResponse)
@handle_grpc_errors
async def takeoff(
    request: TakeoffRequest,
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> StatusResponse:
    logger.debug(f"Takeoff command received: altitude={request.altitude}")

    altitude_msg = altitude_data(data=request.altitude)
    grpc_client.nav_cmd_takeoff(
        altitude_msg,
        [
            ("client-id", "grpc-sync|REST"),
        ],
    )

    return StatusResponse(
        status="success",
        details=f"Takeoff to {request.altitude}m initiated",
    )


@router.post("/land", response_model=StatusResponse)
@handle_grpc_errors
async def land(
    request: LandRequest,
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> StatusResponse:
    logger.debug("Landing command was called")

    grpc_client.nav_cmd_land(
        get_request(req="REST"),
        [
            ("client-id", "grpc-sync|REST"),
        ],
    )

    return StatusResponse(
        status="success",
        details="Landing initiated",
    )


@router.post("/move", response_model=StatusResponse)
@handle_grpc_errors
async def move(
    request: MoveRequest,
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> StatusResponse:
    logger.info(f"Move command received: x={request.x}, y={request.y}, z={request.z}")

    position_msg = vector3(x=request.x, y=request.y, z=request.z)
    grpc_client.nav_cmd_move(
        position_msg,
        [
            ("client-id", "grpc-sync|REST"),
        ],
    )

    coords = f"({request.x}, {request.y})"
    return StatusResponse(
        status="success",
        details=f"Move to {coords} initiated",
    )


@router.post("/speed", response_model=StatusResponse)
@handle_grpc_errors
async def speed(
    request: VelocityRequest,
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
) -> StatusResponse:
    logger.debug(f"Speed command: vx={request.vx}, vy={request.vy}")

    speed_msg = vector2(x=request.vx, y=request.vy)
    grpc_client.nav_cmd_velocity(
        speed_msg,
        [
            ("client-id", "grpc-sync|REST"),
        ],
    )

    spd_str = f"({request.vx}, {request.vy})"
    return StatusResponse(
        status="success",
        details=f"Velocity {spd_str} initiated",
    )
