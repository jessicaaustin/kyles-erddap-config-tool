# NOTE: This repo is published as documentation only

The code is intimately tied with axiom infrastructure, and is not very useful other than as an example. If/when someone develops a similar but generic tool we'll post it here.

## ERDDAP Content

Generate the final ERDDAP content for a specific region or all regions

#### Generating

```bash
docker build -t erddap-content .
docker run -v $(pwd)/output:/output erddap-content  # all regions
docker run -v $(pwd)/output:/output erddap-content bash generate_region [region]  # specific region
```

The ERDDAP config will be in `$(pwd)/output/[region]`

#### Running GenerateDatasetsXml.sh

Run the *axiom/docker-erddap* docker image:

```
# this assumes your datasets are under /mnt/store somewhere
docker run --rm --name erddap-generate-datasets -v /mnt/store:/mnt/store axiom/docker-erddap
```

Then in another terminal, connect to this image and run the script:

```
$ docker exec -it erddap-generate-datasets bash
root@1375a6083670:/usr/local/tomcat# cd webapps/erddap/WEB-INF/
root@1375a6083670:/usr/local/tomcat/webapps/erddap/WEB-INF# chmod +x GenerateDatasetsXml.sh
root@1375a6083670:/usr/local/tomcat/webapps/erddap/WEB-INF# ./GenerateDatasetsXml.sh 
```

#### Testing Locally

1.  Make files in: `regions/testing/datasets/*.xml`.
2.  Build image: `docker build -t erddap-content .`.
3.  Generate the `testing` region: `docker run -v $(pwd)/output:/output erddap-content bash generate_region testing`.
4.  Run ERDDAP: `docker run -d --name erddap-content-testing -v $(pwd)/output/testing:/usr/local/tomcat/content/erddap/ -v /mnt/store:/mnt/store -p 33333:8080 registry.axiom/erddap-axiom:latest`

#### Reserved names:

Don't name your `.xml` files any of these:

* `regions/*/datasets/0050_regional_stations.xml`
* `regions/*/datasets/007*.xml`
