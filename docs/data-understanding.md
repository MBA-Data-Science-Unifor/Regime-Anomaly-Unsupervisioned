# Data Understanding

## Unit of analysis

The expected unit is a network communication flow. The grain, keys, and presence of
repeated records must be confirmed in `01_EDA.ipynb`.

## Feature groups

| Group | Examples |
| --- | --- |
| Identification | record index, source port, and destination port |
| Context | protocol and service |
| Volume | forwarded and received packets and bytes |
| Rate | packets and payload per second |
| Control | FIN, SYN, RST, ACK, PSH, URG, CWR, and ECE flags |
| Temporal | duration, IAT, and active and idle periods |
| Windows | initial and final window sizes |
| External reference | `Attack_type` |

## Points that still require verification

- data types inferred by pandas;
- missing or infinite values;
- constant or nearly constant columns;
- duplicate records;
- skewness and substantially different scales;
- categorical feature cardinality;
- traffic-type distribution;
- possible information leakage.

No quantitative conclusion is recorded here before the reviewed EDA is executed.
