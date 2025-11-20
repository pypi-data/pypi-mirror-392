import base64
import time
from typing import Any, Dict, Optional, Tuple
from urllib import request

import grpc
from lupa import LuaRuntime, lua_type

from ara_api_lua._utils.communication.grpc.messages.base_msg_pb2 import (
    get_request,
    vector2,
    vector3,
)
from ara_api_lua._utils.communication.grpc.messages.msp_msg_pb2 import (
    altitude_data,
    analog_data,
    attitude_data,
    motor_data,
    optical_flow_data,
    position_data,
)
from ara_api_lua._utils.communication.grpc.messages.vision_msg_pb2 import (
    aruco,
    blob,
    qr_code,
)
from ara_api_lua._utils.communication.grpc_sync import gRPCSync

lua = None


def set_lua_runtime(runtime: LuaRuntime) -> None:
    """Устанавливает глобальный LuaRuntime для table_from"""
    global lua
    lua = runtime


class ARALinkLUA:
    def __init__(self):
        self.grpc = gRPCSync()

    # === Вспомогательные методы ===
    def _ok(self, data: Any) -> Tuple[Any, None]:
        return data, None

    def _err(self, e: Exception) -> Tuple[None, str]:
        return None, str(e)

    # === MSP (телеметрия) ===
    def get_imu_data(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            response = self.grpc.msp_get_raw_imu()
            result = {
                "gyro": {
                    "x": response.gyro.x,
                    "y": response.gyro.y,
                    "z": response.gyro.z,
                },
                "acc": {"x": response.acc.x, "y": response.acc.y, "z": response.acc.z},
                "mag": {"x": response.mag.x, "y": response.mag.y, "z": response.mag.z}
                if response.HasField("mag")
                else None,
            }
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_attitude(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            response = self.grpc.msp_get_attitude()
            result = {
                "roll": response.data.x,
                "pitch": response.data.y,
                "yaw": response.data.z,
            }
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_altitude(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            response = self.grpc.msp_get_altitude()
            result = {"data": response.data}
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_position(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            response = self.grpc.msp_get_position()
            result = {"x": response.data.x, "y": response.data.y, "z": response.data.z}
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_optical_flow(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            response = self.grpc.msp_get_optical_flow()
            result = {
                "quality": response.quality,
                "flow_rate": {"x": response.flow_rate.x, "y": response.flow_rate.y},
                "body_rate": {"x": response.body_rate.x, "y": response.body_rate.y},
            }
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_motor(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            response = self.grpc.msp_get_motor()
            result = {"data": list(response.data)}
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_analog(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            response = self.grpc.msp_get_analog()
            result = {
                "voltage": response.voltage,
                "mAh_drawn": response.mAhdrawn,
                "rssi": response.rssi,
                "amperage": response.amperage,
            }
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    # === Navigation (управление) ===
    def takeoff(self, altitude: float) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            response = altitude_data(data=altitude)
            resp = self.grpc.nav_cmd_takeoff(response)
            return self._ok({"status": resp.status})
        except Exception as e:
            return self._err(e)

    def land(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            response = self.grpc.nav_cmd_land(get_request(req="SyncCall"))
            return self._ok({"status": response.status})
        except Exception as e:
            return self._err(e)

    def move_to(
        self, x: float, y: float, z: float
    ) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            request = vector3(x=x, y=y, z=z)
            response = self.grpc.nav_cmd_move(request)
            return self._ok({"status": response.status})
        except Exception as e:
            return self._err(e)

    def set_velocity(
        self, vx: float, vy: float
    ) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            request = vector2(x=vx, y=vy)
            response = self.grpc.nav_cmd_velocity(request)
            return self._ok({"status": response.status})
        except Exception as e:
            return self._err(e)

    def set_altitude(self, altitude: float) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            request = altitude_data(data=altitude)
            response = self.grpc.nav_cmd_altitude(request)
            return self._ok({"status": response.status})
        except Exception as e:
            return self._err(e)

    # === Vision (зрение) ===
    def get_image(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            response = self.grpc.vision_get_image()
            result = {
                "width": response.width,
                "height": response.height,
                "data": response.data,
                "noise": response.noise,
            }
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_aruco_markers(self) -> Tuple[Optional[Any], Optional[str]]:
        if lua is None:
            return None, "Lua runtime not initialized"
        try:
            response = self.grpc.vision_get_aruco()
            markers = []
            for m in response.markers:
                markers.append(
                    {
                        "id": m.id,
                        "position": {
                            "x": m.position.x,
                            "y": m.position.y,
                            "z": m.position.z,
                        },
                        "orientation": {
                            "x": m.orientation.x,
                            "y": m.orientation.y,
                            "z": m.orientation.z,
                        },
                    }
                )
            return lua.table_from(markers), None
        except Exception as e:
            return None, str(e)

    def get_qr_codes(self) -> Tuple[Optional[Any], Optional[str]]:
        if lua is None:
            return None, "Lua runtime not initialized"
        try:
            response = self.grpc.vision_get_qr_code()
            codes = []
            for c in response.codes:
                codes.append(
                    {"data": c.data, "position": {"x": c.position.x, "y": c.position.y}}
                )
            return lua.table_from(codes), None
        except Exception as e:
            return None, str(e)

    def get_blobs(self) -> Tuple[Optional[Any], Optional[str]]:
        if lua is None:
            return None, "Lua runtime not initialized"
        try:
            response = self.grpc.vision_get_blob()
            blobs = []
            for b in response.blobs:
                blobs.append(
                    {
                        "id": b.id,
                        "position": {"x": b.position.x, "y": b.position.y},
                        "size": b.size,
                    }
                )
            return lua.table_from(blobs), None
        except Exception as e:
            return None, str(e)

    # === Утилиты ===
    def sleep(self, seconds: float) -> None:
        time.sleep(seconds)

    def close(self) -> None:
        """Заглушка — в mock-среде ничего не закрываем"""
        pass
