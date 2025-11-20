from functools import wraps
from typing import Optional

import grpc
from fastapi import HTTPException

from ara_api_web._utils.communication.gRPCSync import gRPCSync
from ara_api_web._utils.logger import Logger

_grpc_client: Optional[gRPCSync] = None
_logger: Optional[Logger] = None


def init_dependencies(grpc: gRPCSync, logger: Logger):
    """Вызывается один раз при старте процесса"""
    global _grpc_client, _logger
    _grpc_client = grpc
    _logger = logger


def get_logger() -> Logger:
    if _logger is None:
        raise RuntimeError("Logger not initialized")
    return _logger


def get_grpc_client() -> gRPCSync:
    """Dependency для FastAPI"""
    if _grpc_client is None:
        raise HTTPException(status_code=500, detail="gRPC client not initialized")
    return _grpc_client


def handle_grpc_errors(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except grpc.RpcError as e:
            logger = _logger
            if logger:
                logger.error(f"gRPC error in {func.__name__}: {e}")
            raise HTTPException(status_code=500, detail=f"gRPC error: {str(e)}")
        except HTTPException:
            raise
        except Exception as e:
            logger = _logger
            if logger:
                logger.error(f"Error in {func.__name__}: {e}")
            raise HTTPException(status_code=500, detail=str(e))

    return wrapper
