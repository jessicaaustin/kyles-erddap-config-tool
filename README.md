## ERDDAP Content

Generate the final ERDDAP content for a specific region or all regions

#### Generating

```bash
$ docker build -t erddap-content .
$ docker run -v $(pwd)/output:/output erddap-content  # all regions
$ docker run -v $(pwd)/output:/output erddap-content bash generate_region [region]  # specific region
```

The ERDDAP config will be in `$(pwd)/output/[region]`

