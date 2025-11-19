#!/usr/bin/env python3
"""
NEXUSVIEW: a simple command-line viewer for NeXus files
USAGE: python nxview.py myfile.nxs
"""
import argparse  # type: ignore

# custom class to read Nexus files
from nexusview.h5reader import H5reader

def main():
    # Parsing input options
    PARSER = argparse.ArgumentParser(
        prog="nxview",
        description="A simple command-line viewer for NeXus files",
        epilog="2022 - Nicolas Soler - Alba Synchrotron",
    )

    PARSER.add_argument(
        "hdf5_file", help="hdf5 input file (ideally NeXus)"
    )  # positional argument
    PARSER.add_argument(
        "-c",
        "--csv",
        action="store_true",
        default=False,
        help="Export metadata to a csv file",
    )

    ARGS = PARSER.parse_args()

    # Check the file extension
    extension = ARGS.hdf5_file.split(".")[-1].lower() 

    # Main functionality
    if extension in  ("nxs", "nxs.h5", "h5", "hdf5", "hdf"):
        print(f"Reading {ARGS.hdf5_file}...")
        H5_READER = H5reader(ARGS.hdf5_file)
        H5_READER.read()

        # Output a csv file with all metadata from the NeXus input file
        if ARGS.csv:
            H5_READER.create_csv()
    else:
        print(f"Error: {ARGS.hdf5_file} does not have a NeXus/HDF5 extension. Please rename it as *.nxs or *.h5")
        return



if __name__ == "__main__":
    main()
