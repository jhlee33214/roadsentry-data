# Road binary format v1

This document describes the complete offered road database, not an app API.
Database: ODbL 1.0; contents: DbCL 1.0. See NOTICE.txt.

All numbers use little-endian byte order. Coordinates use WGS84 latitude
and longitude as signed integers in units of 0.00001 degree. The file has
no magic bytes, embedded timestamps, strings, IDs or compression header.
The downloadable `.gz` file is a gzip wrapper around these exact bytes.

| Offset in file | Type | Meaning |
|---|---|---|
| 0 | uint32 | Number of consecutive polyline records |
| 4 | records | Records described below, with no padding or trailer |

Each record is:

| Field | Type | Meaning |
|---|---|---|
| metadata | uint8 | Bit fields below |
| name_hash | uint16 | Opaque road-name/reference fingerprint; 0 may mean absent |
| point_count | uint16 | Number of points, at least 2 |
| first_latitude | int32 | Initial latitude in 1e-5 degrees |
| first_longitude | int32 | Initial longitude in 1e-5 degrees |
| deltas | repeated int16, int16 | `point_count - 1` latitude/longitude delta pairs |

Add each signed delta to the preceding decoded integer coordinate. A
record occupies `13 + 4 * (point_count - 1)` bytes. Convert coordinates to
degrees by dividing by 100000. GeoJSON reverses each pair to longitude,
latitude. Record index is only an index in this file, not an OSM way ID.
A source road can be represented by more than one polyline record.

Metadata:

- Bits 0–2: road class. 1 motorway/link; 2 trunk/link; 3 primary/link;
  4 secondary/link; 5 tertiary/link; 6 unclassified/residential;
  7 living_street/service. Values are classifications of the source data,
  not a guarantee of legal access or current driving conditions.
- Bit 3: one-way in stored point order when set; otherwise no one-way
  restriction is encoded by this format.
- Bits 4–5: simplified vertical category: 0 general/ground, 1 bridge or
  elevated, 2 tunnel or below ground. This is not the original OSM layer
  number and does not prove connectivity at a crossing.
- Bits 6–7: reserved, zero in this release.

The 16-bit name fingerprint is not unique, cannot restore road names,
and must not be used as a globally unique road identifier. Endpoints have
rounded coordinates rather than OSM node IDs. Geometry is a selected and
simplified extract, so it need not preserve every original feature.

## Read and convert

Python 3.9 or newer, standard library only. Download this folder's files.

```sh
python3 read_roads.py roads-d7e4cebe2c14.bin.gz
python3 read_roads.py roads-d7e4cebe2c14.bin.gz --geojsonl roads.geojsonl
```

The first command validates the structure and prints only counts and the
uncompressed checksum. The second also creates a new file containing one
GeoJSON LineString Feature per line. It never overwrites an existing file.
Features have road_class, oneway, layer_category and name_hash properties.

The reader rejects truncation, inconsistent record/point counts, trailing
bytes, unsupported metadata and invalid coordinate ranges. Input and
decompressed data are limited to 64 MiB. This is a resource limit of the
example reader, not a usage restriction on the database.

To obtain the uncompressed binary with a standard gzip utility:

```sh
gzip -dc roads-d7e4cebe2c14.bin.gz > roads.bin
shasum -a 256 roads.bin roads-d7e4cebe2c14.bin.gz
```

Compare with SHA256SUMS. Source metadata, sizes and counts are also in
manifest.json. The database is available without proprietary decoding
software or the RoadSentry app.
