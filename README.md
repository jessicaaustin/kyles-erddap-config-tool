## ERDDAP Content

```
$ conda create -n erddap-content python=3.5
$ source activate erddap-content
$ conda install -c conda-forge --file requirements.txt
```

**NOTE** You need to do this before commiting in the repo:

```bash
$ bash generate
```

This will auto-generate the `datasets.xml` files required by ERDDAP so we
avoid having to maintain one huge file.

DONT EVER EDIT THESE FILES AS THEY WILL BE OVERWRITTEN:

* `datasets.xml`
* `0050_regional_stations.xml`
