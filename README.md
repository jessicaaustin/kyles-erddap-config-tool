## ERDDAP Content

#### Generating

```bash
$ docker build -t erddap-content .
$ docker run -v $(pwd)/regions:/code/regions erddap-content
```

You can then look at the contents to see what was generated. Don't ever commit
these files as the automated processing will overwrite them:

* `[region]/datasets.xml` (combined file erddap accesses)
* `[region]/datasets/0050_regional_stations.xml` (stations)
* `[region]/datasets/007*.xml` (gliders)


```
$ conda create -n erddap-content python=3.5
$ source activate erddap-content
$ conda install -c conda-forge --file requirements.txt
```
