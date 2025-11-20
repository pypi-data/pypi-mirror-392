import signal
import sys
from typing import Optional

import uvicorn

from ara_api_web._core.app import create_app
from ara_api_web._utils import Logger, gRPCSync, init_dependencies
from ara_api_web._utils.config import LOGGER_CONFIG, REST_CONFIG
from ara_api_web._utils.ui import UI


def run_server(host: Optional[str] = None, port: Optional[int] = None):
    host = host or REST_CONFIG.HOST
    port = port or REST_CONFIG.PORT

    logger = Logger(
        log_level=LOGGER_CONFIG.LOG_LEVEL,
        log_to_file=LOGGER_CONFIG.LOG_TO_FILE,
        log_to_terminal=LOGGER_CONFIG.LOG_TO_TERMINAL,
        log_dir=LOGGER_CONFIG.LOG_DIR,
    )

    logger.debug(f"Starting REST API server on {host}:{port}")

    try:
        grpc = gRPCSync()
    except Exception as e:
        logger.error(f"Failed to initialize gRPC client: {e}")
        sys.exit(-1)

    init_dependencies(grpc=grpc, logger=logger)

    app = create_app()

    grpc_address = "50051, 50052, 50053"
    ui = UI()
    ui.display_startup_banner(host=host, port=port, grpc_address=grpc_address)

    def signal_handler(sig, frame):
        logger.debug(f"Received signal {sig}, shutting down gracefully")
        sys.exit(0)

    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)

    try:
        uvicorn.run(
            app,
            host=host,
            port=port,
            log_level="error",
            access_log=True,
        )
    except Exception as e:
        logger.error(f"Server error: {e}")
        raise
    finally:
        logger.warning("REST API server stopped")


if __name__ == "__main__":
    run_server()
