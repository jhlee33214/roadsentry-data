#!/usr/bin/env python3
"""Read the adjacent road database. Python 3.9+; standard library only.

Reader code: MIT (see READER-LICENSE.txt). Database: ODbL 1.0 / DbCL 1.0.
Defaults to aggregate counts. --geojsonl writes road-only GeoJSON features.
"""
import argparse
import gzip
import hashlib
import json
from pathlib import Path
import struct

MAX_BYTES = 64 * 1024 * 1024


def load(path):
    path = Path(path)
    if path.stat().st_size > MAX_BYTES:
        raise ValueError("Input exceeds reader limit")
    opener = gzip.open if path.suffix == ".gz" else open
    with opener(path, "rb") as stream:
        data = stream.read(MAX_BYTES + 1)
    if len(data) > MAX_BYTES:
        raise ValueError("Uncompressed database exceeds reader limit")
    return data


def records(data):
    if len(data) < 4:
        raise ValueError("Missing record count")
    count = struct.unpack_from("<I", data)[0]
    if count > (len(data) - 4) // 17:
        raise ValueError("Record count cannot fit in input")
    offset = 4
    for index in range(count):
        if offset + 13 > len(data):
            raise ValueError("Truncated record header")
        meta, name_hash, point_count, lat, lon = struct.unpack_from("<BHHii", data, offset)
        offset += 13
        if point_count < 2 or offset + 4 * (point_count - 1) > len(data):
            raise ValueError("Invalid point count or truncated deltas")
        if meta & 0xC0 or not 1 <= (meta & 7) <= 7 or ((meta >> 4) & 3) > 2:
            raise ValueError("Unknown road metadata")
        points = [(lat, lon)]
        for _ in range(point_count - 1):
            dlat, dlon = struct.unpack_from("<hh", data, offset)
            offset += 4
            lat += dlat
            lon += dlon
            points.append((lat, lon))
        if any(not (-9_000_000 <= a <= 9_000_000 and -18_000_000 <= b <= 18_000_000)
               for a, b in points):
            raise ValueError("Coordinate outside WGS84 range")
        yield index, meta, name_hash, points
    if offset != len(data):
        raise ValueError("Unexpected trailing bytes")


def feature(index, meta, name_hash, points):
    return {
        "type": "Feature",
        "id": index,
        "properties": {"road_class": meta & 7, "oneway": bool(meta & 8),
                       "layer_category": (meta >> 4) & 3, "name_hash": name_hash},
        "geometry": {"type": "LineString", "coordinates": [[b / 1e5, a / 1e5] for a, b in points]},
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("database", type=Path, help=".bin or .bin.gz file")
    parser.add_argument("--geojsonl", type=Path, help="Write features to a new file (never overwrite)")
    args = parser.parse_args()
    data = load(args.database)
    ways = points = 0
    # Validate the entire input before creating an output file.
    for _, _, _, geometry in records(data):
        ways += 1
        points += len(geometry)
    if args.geojsonl:
        with args.geojsonl.open("x", encoding="utf-8") as stream:
            for item in records(data):
                stream.write(json.dumps(feature(*item), separators=(",", ":")) + "\n")
    print(json.dumps({"records": ways, "points": points, "segments": points - ways,
                      "uncompressed_bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()}))


if __name__ == "__main__":
    main()
