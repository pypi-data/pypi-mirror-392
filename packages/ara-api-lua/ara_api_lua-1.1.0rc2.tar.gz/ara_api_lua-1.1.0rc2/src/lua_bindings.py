import base64
import time
from typing import Any, Dict, Optional, Tuple

import grpc
from lupa import LuaRuntime, lua_type  # ← Только из lupa

# Protobuf импорты
from src.generated.protos.messages.base_msg_pb2 import get_request, vector3, vector4
from src.generated.protos.messages.base_msg_pb2 import vector2 as proto_vector2
from src.generated.protos.messages.msp_msg_pb2 import (
    altitude_data,
    analog_data,
    attitude_data,
    motor_data,
    optical_flow_data,
    position_data,
)
from src.generated.protos.messages.vision_msg_pb2 import aruco, blob, qr_code
from src.generated.protos.msp_pb2_grpc import MSPManagerStub
from src.generated.protos.navigation_pb2_grpc import NavigationManagerStub
from src.generated.protos.vision_pb2_grpc import VisionManagerStub

# Наш gRPC синглтон
from .grpc_sync import gRPCSync

# Глобальный LuaRuntime (устанавливается из bridge.py)
lua = None


def set_lua_runtime(runtime: LuaRuntime) -> None:
    """Устанавливает глобальный LuaRuntime для table_from"""
    global lua
    lua = runtime


class ARALinkLUA:
    def __init__(self):
        self.sync = gRPCSync()
        self.msp = self.sync.get_msp_stub()
        self.nav = self.sync.get_navigation_stub()
        self.vision = self.sync.get_vision_stub()

    # === Вспомогательные методы ===
    def _ok(self, data: Any) -> Tuple[Any, None]:
        return data, None

    def _err(self, e: Exception) -> Tuple[None, str]:
        return None, str(e)

    # === MSP (телеметрия) ===
    def get_imu_data(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            resp = self.msp.get_raw_imu_rpc(get_request(req="SyncCall"))
            result = {
                "gyro": {"x": resp.gyro.x, "y": resp.gyro.y, "z": resp.gyro.z},
                "acc": {"x": resp.acc.x, "y": resp.acc.y, "z": resp.acc.z},
                "mag": {"x": resp.mag.x, "y": resp.mag.y, "z": resp.mag.z}
                if resp.HasField("mag")
                else None,
            }
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_attitude(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            resp = self.msp.get_attitude_rpc(get_request(req="SyncCall"))
            result = {"roll": resp.data.x, "pitch": resp.data.y, "yaw": resp.data.z}
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_altitude(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            resp = self.msp.get_altitude_rpc(get_request(req="SyncCall"))
            result = {"data": resp.data}
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_position(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            resp = self.msp.get_position_rpc(get_request(req="SyncCall"))
            result = {"x": resp.data.x, "y": resp.data.y, "z": resp.data.z}
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_optical_flow(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            resp = self.msp.get_optical_flow_rpc(get_request(req="SyncCall"))
            result = {
                "quality": resp.quality,
                "flow_rate": {"x": resp.flow_rate.x, "y": resp.flow_rate.y},
                "body_rate": {"x": resp.body_rate.x, "y": resp.body_rate.y},
            }
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_motor(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            resp = self.msp.get_motor_rpc(get_request(req="SyncCall"))
            result = {"data": list(resp.data)}
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_analog(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            resp = self.msp.get_analog_rpc(get_request(req="SyncCall"))
            result = {
                "voltage": resp.voltage,
                "mAh_drawn": resp.mAhdrawn,
                "rssi": resp.rssi,
                "amperage": resp.amperage,
            }
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    # === Navigation (управление) ===
    def takeoff(self, altitude: float) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            req = altitude_data(data=altitude)
            resp = self.nav.cmd_takeoff_rpc(req)
            return self._ok({"status": resp.status})
        except Exception as e:
            return self._err(e)

    def land(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            resp = self.nav.cmd_land_rpc(get_request(req="SyncCall"))
            return self._ok({"status": resp.status})
        except Exception as e:
            return self._err(e)

    def move_to(
        self, x: float, y: float, z: float, yaw: float = 0.0
    ) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            req = vector4(x=x, y=y, z=z, w=yaw)
            resp = self.nav.cmd_move_rpc(req)
            return self._ok({"status": resp.status})
        except Exception as e:
            return self._err(e)

    def set_velocity(
        self, vx: float, vy: float
    ) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            req = proto_vector2(x=vx, y=vy)
            resp = self.nav.cmd_velocity_rpc(req)
            return self._ok({"status": resp.status})
        except Exception as e:
            return self._err(e)

    def set_altitude(self, altitude: float) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            req = altitude_data(data=altitude)
            resp = self.nav.cmd_altitude_rpc(req)
            return self._ok({"status": resp.status})
        except Exception as e:
            return self._err(e)

    # === Vision (зрение) ===
    def get_image(self) -> Tuple[Optional[Dict], Optional[str]]:
        try:
            resp = self.vision.get_image_rpc(get_request(req="SyncCall"))
            data_b64 = base64.b64encode(resp.data).decode() if resp.data else ""
            result = {
                "width": resp.width,
                "height": resp.height,
                "data": data_b64,
                "noise": resp.noise,
            }
            return self._ok(result)
        except Exception as e:
            return self._err(e)

    def get_aruco_markers(self) -> Tuple[Optional[Any], Optional[str]]:
        if lua is None:
            return None, "Lua runtime not initialized"
        try:
            resp = self.vision.get_aruco_rpc(get_request(req="SyncCall"))
            markers = []
            for m in resp.markers:
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
            resp = self.vision.get_qr_rpc(get_request(req="SyncCall"))
            codes = []
            for c in resp.codes:
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
            resp = self.vision.get_blob_rpc(get_request(req="SyncCall"))
            blobs = []
            for b in resp.blobs:
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
