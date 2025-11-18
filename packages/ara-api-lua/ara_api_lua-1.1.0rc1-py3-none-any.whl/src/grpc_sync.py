# ara_lua/grpc_sync.py
import os
import threading
from typing import ClassVar, Dict

import grpc

from generated.protos.msp_pb2_grpc import MSPManagerStub
from generated.protos.navigation_pb2_grpc import NavigationManagerStub
from generated.protos.vision_pb2_grpc import VisionManagerStub


class gRPCSync:
    _instance: ClassVar[Dict[int, "gRPCSync"]] = {}
    _creation_lock: ClassVar[threading.Lock] = threading.Lock()

    def __new__(cls) -> "gRPCSync":
        process_id = os.getpid()
        if process_id not in cls._instance:
            with cls._creation_lock:
                if process_id not in cls._instance:
                    instance = super().__new__(cls)
                    cls._instance[process_id] = instance
        return cls._instance[process_id]

    def __init__(self):
        if hasattr(self, "_initialized"):
            return

        # Создаём каналы
        self.msp_channel = grpc.insecure_channel("localhost:50051")
        self.nav_channel = grpc.insecure_channel("localhost:50052")
        self.vision_channel = grpc.insecure_channel("localhost:50053")

        # Создаём стабы (без @property!)
        self.msp_stub = MSPManagerStub(self.msp_channel)
        self.navigation_stub = NavigationManagerStub(self.nav_channel)
        self.vision_stub = VisionManagerStub(self.vision_channel)

        self._initialized = True

    # Публичные геттеры (без @property — просто методы)
    def get_msp_stub(self):
        return self.msp_stub

    def get_navigation_stub(self):
        return self.navigation_stub

    def get_vision_stub(self):
        return self.vision_stub
 