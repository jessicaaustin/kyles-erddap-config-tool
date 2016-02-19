## ERDDAP Content


Requires the `libxml2-utils` package (for `xmllint`)

**NOTE** You need to do this before commiting in the repo:

```bash
$ bash generate
```

This will auto-generate the `datasets.xml` files required by ERDDAP so we
avoid having to maintain one huge file.

DONT EVER EDIT THESE FILES AS THEY WILL BE OVERWRITTEN:

* `datasets.xml`
* `0050_regional_stations.xml`
