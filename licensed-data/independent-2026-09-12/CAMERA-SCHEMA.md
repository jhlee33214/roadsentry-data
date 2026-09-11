# Camera database format

`cameras-a1053e0c1027.json.gz` contains the complete offered adapted database as
a UTF-8 JSON array compressed with standard gzip.
Each row contains these 13 numeric fields, in order:

| Index | Field | Meaning |
|---|---|---|
| 0 | latitude | WGS84 decimal degrees |
| 1 | longitude | WGS84 decimal degrees |
| 2 | speedLimit | Kilometres per hour |
| 3 | flags | Bit mask described below |
| 4 | sectionLengthM | Section length in metres; 0 if unknown |
| 5 | roadBearingAxis | Road axis in degrees, 0–179; -1 if unknown |
| 6 | roadClass | Road class listed below; 0 if unknown |
| 7 | enforceDir | 0 means no verified enforcement direction in this database |
| 8 | layer | 0 ground/unknown; 1 elevated/bridge; 2 underground/tunnel |
| 9 | nameHash | Opaque road-name/reference fingerprint; 0 may mean absent |
| 10 | originalLatitude | Original public-source latitude; equals field 0 |
| 11 | originalLongitude | Original public-source longitude; equals field 1 |
| 12 | laneGap | Lane separation in metres; 0 if unknown |

Flags: bit 0 (1) section start; bit 1 (2) section end; bit 2 (4) protection
zone; bit 3 (8) signal-only enforcement. Other bits are zero in this database.
A protection zone is not necessarily a school zone.

Road class: 1 motorway/link; 2 trunk/link; 3 primary/link; 4 secondary/link;
5 tertiary/link; 6 unclassified/residential; 7 living_street/service.
A road axis is not an enforcement direction. Name fingerprints can collide and
are not identifiers or a way to restore road names. Unknown values and source
coordinate errors may remain. The data is not a guarantee of road conditions.

Decompress using standard gzip, then read with any JSON library. For example:

```sh
gzip -dc cameras-a1053e0c1027.json.gz > cameras.json
```

The database can be read with any standard JSON library. Its ODbL database
license and the original component notices are described in NOTICE.txt.
