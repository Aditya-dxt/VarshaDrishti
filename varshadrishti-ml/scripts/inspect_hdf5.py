import argparse
import sys
import json
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent))
from src.data.hdf5_reader import INSAT3DRReader

def main():
    parser = argparse.ArgumentParser(description="Inspect INSAT-3DR HDF5 structure.")
    parser.add_argument("file_path", type=str, help="Path to the real HDF5 file.")
    args = parser.parse_args()

    reader = INSAT3DRReader()
    try:
        result = reader.inspect(args.file_path)
        print(json.dumps(result, indent=4))
    except FileNotFoundError as e:
        print(f"ERROR: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
