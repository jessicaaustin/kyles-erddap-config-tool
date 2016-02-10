## ERDDAP Content

**NOTE**
You need to run this before commiting in the repo!

```bash
$ ln -s ./pre-commit .git/hooks/pre-commit
```

This will auto-generate the `datasets.xml` files required by ERDDAP so we
avoid having to maintain one huge file.

