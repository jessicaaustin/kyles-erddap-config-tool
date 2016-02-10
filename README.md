## ERDDAP Content


Requires the `libxml2-utils` package (for `xmllint`)

**NOTE** You need to do this before commiting in the repo:

```bash
$ rm .git/hooks/pre-commit.sample
$ cp ./pre-commit .git/hooks/pre-commit
```

This will auto-generate the `datasets.xml` files required by ERDDAP so we
avoid having to maintain one huge file.

DONT EVER EDIT THE `datasets.xml` FILES. THEY WILL BE OVERWRITTEN.
