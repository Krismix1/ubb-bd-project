#!/usr/bin/env python3
import json
import sys


def read_input(file):
    for line in file:
        # split the line into words
        data = json.loads(line)
        yield data


def main(separator="\t"):
    # input comes from STDIN (standard input)
    data = read_input(sys.stdin)
    for flight in data:
        # write the results to STDOUT (standard output);
        # what we output here will be the input for the
        # Reduce step, i.e. the input for reducer.py

        key = flight["flight_data"]["flight_id"]  # or maybe use aircraft_id
        print("%s%s%s" % (key, separator, json.dumps(flight)))


if __name__ == "__main__":
    main()
