#!/usr/bin/env python3

import json
import math
import sys
from collections import defaultdict
from itertools import groupby
from operator import itemgetter


def read_mapper_output(file, separator="\t"):
    for line in file:
        flight_id, data = line.rstrip().split(separator, 1)
        yield flight_id.strip(), json.loads(data)


def gcdist(lat1, lon1, lat2, lon2):
    # Great Circle Distance Formula
    # https://jpensor.com/great-circle-distance-python/

    # TODO: https://en.wikipedia.org/wiki/Great-circle_distance#Computational_formulas
    # On computer systems with low floating point precision, the spherical law of cosines formula can have large rounding errors if the distance is small (if the two points are a kilometer apart on the surface of the Earth, the cosine of the central angle is near 0.99999999)
    # The haversine formula is numerically better-conditioned for small distances
    # TODO: We might have to use altitude for a more accurate calculation
    # https://stackoverflow.com/questions/11710972/great-circle-distance-plus-altitude-change

    # The radius in KM
    R = 6378.137

    # the formula requires we convert all degrees to radians
    lat1 = math.radians(lat1)
    lat2 = math.radians(lat2)
    lon1 = math.radians(lon1)
    lon2 = math.radians(lon2)

    lat_span = lat1 - lat2
    lon_span = lon1 - lon2

    a = math.sin(lat_span / 2) ** 2
    b = math.cos(lat1)
    c = math.cos(lat2)
    d = math.sin(lon_span / 2) ** 2

    dist = 2 * R * math.asin(math.sqrt(a + b * c * d))

    return dist  # in KM


# https://insight-trucks.com/en/calculate_fuel_consumption/
# https://monroeaerospace.com/blog/what-type-of-fuel-do-airplanes-use/
# With the exception of piston-based airplanes, most airplanes use kerosene fuel
liters_per_km_by_engine_type = defaultdict(lambda: 100)

# https://www.icbe.com/carbondatabase/volumeconverter.asp
# 1 liter kerosene = 0.00255 tonnes of CO2 = 1.444 m^3 of CO2
kerosene_liters_to_co2 = lambda x: x * 0.00255


def compute_fuel(row):
    row["fuel_used_liters"] = (
        liters_per_km_by_engine_type[row.aircraft_number] * row.great_circle_distance
    )
    return row


def compute_diff(group_key, p_df):
    # print("----------------------")
    # print(group_key)
    # print("----------------------")
    # print(p_df)
    p_df["lat_diff"] = p_df.latitude.diff()
    p_df["long_diff"] = p_df.longitude.diff()
    p_df["alt_diff"] = p_df.altitude.diff()
    p_df["has_moved"] = (
        (p_df.lat_diff != 0) | (p_df.long_diff != 0) | (p_df.alt_diff != 0)
    )
    distances = []
    for i in range(len(p_df)):
        if i == len(p_df) - 1:
            gcd = 0
        else:
            df1 = p_df.iloc[i]
            df2 = p_df.iloc[i + 1]
            lat1, long1 = df1.latitude, df1.longitude
            lat2, long2 = df2.latitude, df2.longitude
            gcd = gcdist(lat1, long1, lat2, long2)

        distances.append(gcd)

    p_df["great_circle_distance"] = distances
    p_df = p_df.apply(compute_fuel, axis=1)

    return p_df


def main(separator=","):
    all_data = read_mapper_output(sys.stdin, separator="\t")
    # groupby groups multiple word-count pairs by word,
    # and creates an iterator that returns consecutive keys and their group
    for current_flight, group in groupby(all_data, itemgetter(0)):
        distance = 0
        fuel_used = 0
        for _flight, f_data in group:
            try:
                _, next_data = next(group)
            except StopIteration:
                continue

            lat1, long1 = (
                f_data["flight_data"]["latitude"],
                f_data["flight_data"]["longitude"],
            )
            lat2, long2 = (
                next_data["flight_data"]["latitude"],
                next_data["flight_data"]["longitude"],
            )
            gcd = gcdist(lat1, long1, lat2, long2)
            fuel_used_liters = (
                liters_per_km_by_engine_type[f_data["flight_data"]["aircraft_number"]]
                * gcd
            )
            distance += gcd
            fuel_used += fuel_used_liters

        print(separator.join([str(distance), str(fuel_used), current_flight.strip()]))


if __name__ == "__main__":
    main()
