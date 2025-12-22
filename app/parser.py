import re
import os
from pathlib import Path
# import glob

def get_logs(dir_: Path):
    if not dir_.exists():
        return []
    return list(elem.name for elem in dir_.glob("*/"))


def cat_logs():
    """"""
print(get_logs(Path("app/logs")))