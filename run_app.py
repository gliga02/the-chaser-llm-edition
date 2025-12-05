import pathlib
import sys

BASE_DIR = pathlib.Path(__file__).resolve().parent
SRC_DIR = BASE_DIR / "src"
if str(SRC_DIR) not in sys.path:
    sys.path.insert(0, str(SRC_DIR))

from ui.app import create_app

def main() -> None:
    app = create_app(BASE_DIR)
    app.launch()


if __name__ == "__main__":
    main()