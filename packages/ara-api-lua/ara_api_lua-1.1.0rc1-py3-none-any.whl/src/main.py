import sys
from pathlib import Path

from src.bridge import LuaBridge


def main():
    if len(sys.argv) != 2:
        print("Usage: ara-api-lua <script.lua>")
        sys.exit(1)

    script_path = Path(sys.argv[1])
    if not script_path.exists():
        print(f"Error: {script_path} not found")
        sys.exit(1)

    bridge = LuaBridge()
    bridge.execute_script(str(script_path))


if __name__ == "__main__":
    main()
