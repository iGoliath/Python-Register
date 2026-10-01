import json
from pathlib import Path


class Config:

    def __init__(self):

        current_dir = Path(__file__).parent
        file_path = current_dir / "config.json"

        with open(file_path, "r", encoding="utf-8") as fp:
            self.data = json.load(fp)

    def write_out_config(self):
        with open(
            Path(__file__).parent / "config.json",
            "w",
            encoding="utf-8",
        ) as file:
            json.dump(self.data, file, indent=4)
