# Benchmark Suite

A benchmarking suite for comparing different Python JSON Schema implementations.

## Implementations

- `jsonschema-rs` (latest version in this repo)
- [jsonschema](https://pypi.org/project/jsonschema/) (v4.23.0)
- [fastjsonschema](https://pypi.org/project/fastjsonschema/) (v2.20.0)

## Usage

Install the dependencies:

```console
$ pip install -e ".[bench]"
```

Run the benchmarks:

```console
$ pytest benches/bench.py
```

## Overview

| Benchmark     | Description                                    | Schema Size | Instance Size |
|----------|------------------------------------------------|-------------|---------------|
| OpenAPI  | Zuora API validated against OpenAPI 3.0 schema | 18 KB       | 4.5 MB        |
| Swagger  | Kubernetes API (v1.10.0) with Swagger schema   | 25 KB       | 3.0 MB        |
| GeoJSON  | Canadian border in GeoJSON format              | 4.8 KB      | 2.1 MB        |
| CITM     | Concert data catalog with inferred schema      | 2.3 KB      | 501 KB        |
| Fast     | From fastjsonschema benchmarks (valid/invalid) | 595 B       | 55 B / 60 B   |
| FHIR     | Patient example validated against FHIR schema  | 3.3 MB      | 2.1 KB        |

Sources:
- OpenAPI: [Zuora](https://github.com/APIs-guru/openapi-directory/blob/1afd351ddf50e050acdb52937a819ef1927f417a/APIs/zuora.com/2021-04-23/openapi.yaml), [Schema](https://spec.openapis.org/oas/3.0/schema/2021-09-28)
- Swagger: [Kubernetes](https://raw.githubusercontent.com/APIs-guru/openapi-directory/master/APIs/kubernetes.io/v1.10.0/swagger.yaml), [Schema](https://github.com/OAI/OpenAPI-Specification/blob/main/_archive_/schemas/v2.0/schema.json)
- GeoJSON: [Schema](https://geojson.org/schema/FeatureCollection.json)
- CITM: Schema inferred via [infers-jsonschema](https://github.com/Stranger6667/infers-jsonschema)
- Fast: [fastjsonschema benchmarks](https://github.com/horejsek/python-fastjsonschema/blob/master/performance.py#L15)
- FHIR: [Schema](http://hl7.org/fhir/R4/fhir.schema.json.zip) (R4 v4.0.1), [Example](http://hl7.org/fhir/R4/patient-example-d.json.html)

## Results

### Comparison with Other Libraries

| Benchmark     | fastjsonschema | jsonschema    | jsonschema-rs (validate) |
|---------------|----------------|---------------|----------------|
| OpenAPI       | - (1)          | 533.80 ms (**x72.88**) | 7.3264 ms     |
| Swagger       | - (1)          | 970.32 ms (**x193.34**)| 5.0193 ms     |
| Canada (GeoJSON) | 9.521 ms (**x3.88**)  | 738.28 ms (**x300.61**) | 2.4559 ms |
| CITM Catalog  | 4.0752 ms (**x2.85**)   | 76.05 ms (**x53.26**) | 1.4281 ms  |
| Fast (Valid)  | 1.933 µs (**x6.90**)   | 32.124 µs (**x114.75**) | 279.95 ns  |
| Fast (Invalid)| 2.073 µs (**x4.24**)   | 32.245 µs (**x65.89**) | 489.35 ns  |
| FHIR          | 1.9352 ms (**x452.40**)   | 11.463 ms (**x2679.55**) | 4.2780 µs  |

Notes:

1. `fastjsonschema` fails to compile the Open API spec due to the presence of the `uri-reference` format (that is not defined in Draft 4). However, unknown formats are explicitly supported by the spec.

You can find benchmark code in [benches/](benches/), Python version `3.14.0`, Rust version `1.91.1`.

## Contributing

Contributions to improve, expand, or optimize the benchmark suite are welcome. This includes adding new benchmarks, ensuring fair representation of real-world use cases, and optimizing the configuration and usage of benchmarked libraries. Such efforts are highly appreciated as they ensure accurate and meaningful performance comparisons.
