import re
from pathlib import Path

import numpy as np
import pandas as pd

CC_PATTERN = re.compile(r"cycle[\s_-]*count\s*[:=]?\s*(\d+)", re.IGNORECASE)


def list_raw_files():
    base = Path(Path(__file__).resolve().parent.parent.parent.parent)
    data_file = base / "common" / "RM3100-sensor-reading" / "data" / "raw"
    return data_file, sorted(data_file.rglob("rm3100_*.txt"))



def read_cycle_count_file(path: Path):
    with open(path, encoding = "utf-8") as f:
        for line in f:
            if not line.startswith('#'):
                break
            match = CC_PATTERN.search(line)
            if match:
                return int(match.group(1))

    match = re.search(r"(\d+)", path.parent.name)
    return int(match.group(1)) if match else np.nan


def processed_file(path: Path, start = 10, end = 110):
    df = pd.read_csv(path, comment = "#")
    df = df[start:end].reset_index(drop = True)
    df = df.drop(columns = "t_us")
    df.attrs["CC"] = read_cycle_count_file(path)
    df.attrs["file"] = path.name
    return df