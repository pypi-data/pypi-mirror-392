"""Lua bridge for executing Lua scripts with ARA API."""

import time

import lupa
from lupa import LuaRuntime

from ara_api_lua._core.adapters import ARALinkLUA, set_lua_runtime
from ara_api_lua._utils import gRPCSync, logger


class LuaBridge:
    def __init__(self, logger: logger):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.api = ARALinkLUA()

        self._logger = logger

        set_lua_runtime(self.lua)

        self.lua.globals()["ara"] = self.api
        self.lua.globals()["sleep"] = time.sleep

    def execute(self, filepath: str) -> None:
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                script = f.read()
            self.lua.execute(script)
        except lupa.LuaError as e:
            print(f"Lua Error: {e}")
        except Exception as e:
            print(f"Error: {e}")

    def close(self) -> None:
        self._channel_factory.close_all()
