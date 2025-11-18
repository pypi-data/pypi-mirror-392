import json
import pandas as pd
from importlib import resources

def _load_jsonl(package: str, file: str):
    with resources.open_text(package, file, encoding="utf-8") as f:
        return [json.loads(line) for line in f]

def load_colleges_df():
    data = _load_jsonl(__package__ + ".resources", "normalized_colleges.jsonl")
    return pd.DataFrame(data)

def load_branches_df():
    data = _load_jsonl(__package__ + ".resources", "normalized_branches.jsonl")
    return pd.DataFrame(data)
