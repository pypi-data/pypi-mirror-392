import argparse
import json
from . import extract_resume

def main():
    parser = argparse.ArgumentParser(description="Extract structured data from a resume PDF.")
    parser.add_argument("file", help="Path to the resume PDF")

    args = parser.parse_args()

    data = extract_resume(args.file)
    print(json.dumps(data, indent=4))
