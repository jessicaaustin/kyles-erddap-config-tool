## ERDDAP Content

Generate the final ERDDAP content for a specific region or all regions

#### Generating

```bash
$ docker build -t erddap-content .
$ docker run -v $(pwd)/output:/output erddap-content  # all regions
$ docker run -v $(pwd)/output:/output erddap-content bash generate_region [region]  # specific region
```

The ERDDAP config will be in `$(pwd)/output/[region]`


#### Testing Locally

1.  Make files in: `regions/testing/datasets/*.xml`.
2.  Build image: `docker build -t erddap-content .`.
3.  Generate the `testing` region: `docker run -v $(pwd)/output:/output erddap-content bash generate_region testing`.
4.  Run ERDDAP: `docker run -d --name erddap-content-testing -v $(pwd)/output/testing:/usr/local/tomcat/content/erddap/ -p 33333:8080 registry.axiom/erddap-axiom:latest`

#### Reserved names:

Don't name your `.xml` files any of these:

* `regions/*/datasets/0050_regional_stations.xml`
* `regions/*/datasets/007*.xml`
