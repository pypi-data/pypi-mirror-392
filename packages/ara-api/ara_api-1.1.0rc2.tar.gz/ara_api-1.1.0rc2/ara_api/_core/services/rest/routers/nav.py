from fastapi import APIRouter, Depends

from ara_api._core.services.rest.models import (
    LandRequest,
    MoveRequest,
    StatusResponse,
    TakeoffRequest,
    VelocityRequest,
)
from ara_api._core.services.rest.routers._helpers import (
    get_grpc_client,
    get_logger,
    handle_grpc_errors,
)

router = APIRouter(prefix="/api/navigation", tags=["Navigation"])


@router.post("/takeoff", response_model=StatusResponse)
@handle_grpc_errors
async def takeoff(
    request: TakeoffRequest,
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
):
    logger.debug(f"Takeoff command received: altitude={request.altitude}")

    altitude_msg = Altitude(alt=request.altitude)
    grpc_client.nav_cmd_takeoff(
        altitude_msg.grpc,
        [
            ("source", "test-cmd"),
            ("client-id", "grpc-sync"),
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
):
    logger.debug("Landing command was called")

    grpc_client.nav_cmd_land(
        [
            ("source", "test-cmd"),
            ("client-id", "grpc-sync"),
        ],
    )

    return StatusResponse(
        status="success",
        details="Landing initiated",
    )


@router.post("/move", response_model=StatusResponse)
@handle_grpc_errors
async def move(
    request: TakeoffRequest,
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
):
    logger.debug(f"Takeoff command received: altitude={request.altitude}")

    altitude_msg = Altitude(alt=request.altitude)
    grpc_client.nav_cmd_takeoff(
        altitude_msg.grpc,
        [
            ("source", "test-cmd"),
            ("client-id", "grpc-sync"),
        ],
    )

    return StatusResponse(
        status="success",
        details=f"Takeoff to {request.altitude}m initiated",
    )
