import time

import lupa
from lupa import LuaRuntime

from src.lua_bindings import ARALinkLUA, set_lua_runtime


class LuaBridge:
    def __init__(self):
        self.lua = LuaRuntime(unpack_returned_tuples=True)
        self.api = ARALinkLUA()

        # ← Передаём runtime в lua_bindings
        set_lua_runtime(self.lua)

        # Регистрируем в Lua
        self.lua.globals()["ara"] = self.api
        self.lua.globals()["sleep"] = time.sleep

    def execute_script(self, filepath: str):
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                script = f.read()
            self.lua.execute(script)
        except lupa.LuaError as e:
            print(f"Lua Error: {e}")
        except Exception as e:
            print(f"Error: {e}")
