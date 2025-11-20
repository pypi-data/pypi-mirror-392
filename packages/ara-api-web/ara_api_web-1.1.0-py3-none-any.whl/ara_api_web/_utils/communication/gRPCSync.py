import os
import threading
from typing import ClassVar, Dict, Optional

import grpc

from ara_api_web._utils.communication.grpc.messages.base_msg_pb2 import (
    get_request,
)
from ara_api_web._utils.communication.grpc.messages.msp_msg_pb2 import (
    altitude_data,
    analog_data,
    attitude_data,
    imu_data,
    motor_data,
    optical_flow_data,
    position_data,
    sonar_data,
    velocity_data,
)
from ara_api_web._utils.communication.grpc.messages.vision_msg_pb2 import (
    aruco_data_array,
    blob_data_array,
    image_data,
    qr_data_array,
)
from ara_api_web._utils.communication.grpc.msp_pb2_grpc import MSPManagerStub
from ara_api_web._utils.communication.grpc.navigation_pb2_grpc import (
    NavigationManagerStub,
)
from ara_api_web._utils.communication.grpc.vision_pb2_grpc import VisionManagerStub
from ara_api_web._utils.config import (
    LOGGER_CONFIG,
    MSPConfigGRPC,
    NavigationConfigGRPC,
    VisionConfigGRPC,
)
from ara_api_web._utils.decorators import grpc_error_handler
from ara_api_web._utils.logger import Logger


class gRPCSync:
    _instance: ClassVar[Dict[int, "gRPCSync"]] = {}
    _creation_lock: ClassVar[threading.Lock] = threading.Lock()
    _logger = Logger(
        log_level=LOGGER_CONFIG.LOG_LEVEL,
        log_to_file=LOGGER_CONFIG.LOG_TO_FILE,
        log_to_terminal=LOGGER_CONFIG.LOG_TO_TERMINAL,
        log_dir=LOGGER_CONFIG.LOG_DIR,
    )

    def __new__(cls) -> "gRPCSync":
        process_id = os.getpid()

        if process_id not in cls._instance:
            with cls._creation_lock:
                if process_id not in cls._instance:
                    instance = super().__new__(cls)
                    cls._instance[process_id] = instance
                    cls._logger.debug(
                        "gRPCSync instance created for process ID: {process_id}".format(
                            process_id=process_id
                        )
                    )

        return cls._instance[process_id]

    def __init__(self):
        if hasattr(self, "_initialized"):
            self._logger.debug(
                "gRPCSync instance already "
                "initialized for process ID: {process_id}".format(
                    process_id=os.getpid()
                )
            )
            return

        try:
            self._init_msp_connection()
            self._init_navigation_connection()
            self._init_vision_connection()

        except Exception as e:
            self._logger.error(f"Failed to initialize gRPC connections: {e}")
            self._cleanup_all_connections()

        self._initialized: bool = True

    def __del__(self):
        try:
            self._cleanup_all_connections()
        except Exception:
            pass  # Skip cleanup errors

    def _init_msp_connection(self) -> None:
        msp_address: str = MSPConfigGRPC.HOST + ":" + MSPConfigGRPC.PORT

        self._msp_channel = grpc.insecure_channel(msp_address)
        self._msp_stub = MSPManagerStub(self._msp_channel)

        self._logger.debug(
            "gRPCSync MSP connection initialized with address: {msp_address}".format(
                msp_address=msp_address
            )
        )

    def _init_navigation_connection(self) -> None:
        navigation_address: str = (
            NavigationConfigGRPC.HOST + ":" + NavigationConfigGRPC.PORT
        )

        self._navigation_channel = grpc.insecure_channel(navigation_address)
        self._navigation_stub = NavigationManagerStub(self._navigation_channel)

        self._logger.debug(
            "gRPCSync Navigation connection initialized"
            " with address: {navigation_address}".format(
                navigation_address=navigation_address
            )
        )

    def _init_vision_connection(self) -> None:
        vision_address: str = VisionConfigGRPC.HOST + ":" + VisionConfigGRPC.PORT

        self._vision_channel = grpc.insecure_channel(vision_address)
        self._vision_stub = VisionManagerStub(self._vision_channel)

        self._logger.debug(
            "gRPCSync Vision connection initialized"
            " with address: {vision_address}".format(vision_address=vision_address)
        )

    def _cleanup_all_connections(self) -> None:
        channels = [
            getattr(self, "_msp_channel", None),
            getattr(self, "_navigation_channel", None),
            getattr(self, "_vision_channel", None),
        ]

        for channel in channels:
            if channel:
                try:
                    channel.close()
                except Exception:
                    self._logger.error(
                        "gRPCSync cleanup failed for process ID: {process_id}".format(
                            process_id=os.getpid()
                        )
                    )

    @classmethod
    def get_instance(cls) -> "gRPCSync":
        return cls()

    @grpc_error_handler()
    def msp_get_raw_imu(self) -> Optional[imu_data]:
        return self._msp_stub.get_raw_imu_rpc(get_request(req="SyncCall"))

    @grpc_error_handler()
    def msp_get_motor(self) -> Optional[motor_data]:
        return self._msp_stub.get_motor_rpc(get_request(req="SyncCall"))

    @grpc_error_handler()
    def msp_get_attitude(self) -> Optional[attitude_data]:
        return self._msp_stub.get_attitude_rpc(get_request(req="SyncCall"))

    @grpc_error_handler()
    def msp_get_altitude(self) -> Optional[altitude_data]:
        return self._msp_stub.get_altitude_rpc(get_request(req="SyncCall"))

    @grpc_error_handler()
    def msp_get_sonar(self) -> Optional[sonar_data]:
        return self._msp_stub.get_sonar_rpc(get_request(req="SyncCall"))

    @grpc_error_handler()
    def msp_get_optical_flow(self) -> Optional[optical_flow_data]:
        return self._msp_stub.get_optical_flow_rpc(get_request(req="SyncCall"))

    @grpc_error_handler()
    def msp_get_position(self) -> Optional[position_data]:
        return self._msp_stub.get_position_rpc(get_request(req="SyncCall"))

    @grpc_error_handler()
    def msp_get_velocity(self) -> Optional[velocity_data]:
        return self._msp_stub.get_velocity_rpc(get_request(req="SyncCall"))

    @grpc_error_handler()
    def msp_get_analog(self) -> Optional[analog_data]:
        return self._msp_stub.get_analog_rpc(get_request(req="SyncCall"))

    @grpc_error_handler()
    def msp_cmd_send_rc(self, request, context=None) -> None:
        self._msp_stub.cmd_send_rc_rpc(request)

    @grpc_error_handler()
    def msp_cmd_zero_position(self, request, context=None) -> None:
        self._msp_stub.cmd_zero_position_rpc(request)

    @grpc_error_handler()
    def nav_cmd_takeoff(self, request, context=None) -> None:
        return self._navigation_stub.cmd_takeoff_rpc(request, metadata=context)

    @grpc_error_handler()
    def nav_cmd_land(self, request, context=None) -> None:
        return self._navigation_stub.cmd_land_rpc(request, metadata=context)

    @grpc_error_handler()
    def nav_cmd_move(self, request, context=None) -> None:
        return self._navigation_stub.cmd_move_rpc(request, metadata=context)

    @grpc_error_handler()
    def nav_cmd_velocity(self, request, context=None) -> None:
        return self._navigation_stub.cmd_velocity_rpc(request, metadata=context)

    @grpc_error_handler()
    def nav_cmd_altitude(self, request, context=None) -> None:
        return self._navigation_stub.cmd_altitude_rpc(request, metadata=context)

    @grpc_error_handler()
    def vision_get_image(self) -> Optional[image_data]:
        return self._vision_stub.get_image_rpc(get_request(req="SyncCall"))

    @grpc_error_handler()
    def vision_get_image_stream(self) -> None:
        raise NotImplementedError("Cant load image stream")

    @grpc_error_handler()
    def vision_get_aruco(self) -> Optional[aruco_data_array]:
        return self._vision_stub.get_aruco_rpc(get_request(req="SyncCall"))

    @grpc_error_handler()
    def vision_get_qr_code(self) -> Optional[qr_data_array]:
        return self._vision_stub.get_qr_rpc(get_request(req="SyncCall"))

    @grpc_error_handler()
    def vision_get_blob(self) -> Optional[blob_data_array]:
        return self._vision_stub.get_blob_rpc(get_request(req="SyncCall"))
