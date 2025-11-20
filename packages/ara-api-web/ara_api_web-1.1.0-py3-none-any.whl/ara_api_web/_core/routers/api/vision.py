from fastapi import APIRouter, Depends

from ara_api_web._utils import (
    get_grpc_client,
    get_logger,
    handle_grpc_errors,
)

router = APIRouter(prefix="/api/vision", tags=["Vision"])


@router.get("/image")
@handle_grpc_errors
async def get_image(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
):
    logger.debug("Image request received")
    return {"status": "not_implemented", "message": "Image API coming soon"}


@router.get("/aruco")
@handle_grpc_errors
async def get_aruco(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
):
    logger.debug("Aruco request received")
    return {"status": "not_implemented", "message": "Aruco API coming soon"}


@router.get("/qr")
@handle_grpc_errors
async def get_qr(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
):
    logger.debug("QR code request received")
    return {
        "status": "not_implemented",
        "message": "QR code API coming soon",
    }


@router.get("/blob")
@handle_grpc_errors
async def get_blob(
    grpc_client=Depends(get_grpc_client),
    logger=Depends(get_logger),
):
    logger.debug("Blob request received")
    return {"status": "not_implemented", "message": "Blob API coming soon"}
