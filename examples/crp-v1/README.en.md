# Minimal CRP v1 archive example

This directory demonstrates the archive layout currently accepted by
`CheeseWAF/internal/crp.ParseArchive`. It is not an installable plugin: the
`signatures/manifest.json` file contains an empty array and no real private key
or signature.

Create an archive from this directory by selecting only the three files below.
Do not run `zip -r .`; that would include this README and the v1 parser would
reject the unknown entry.

```sh
zip -X demo-v1.crp manifest.json artifact/payload.txt signatures/manifest.json
unzip -l demo-v1.crp
```

The archive should contain exactly:

```text
manifest.json
artifact/payload.txt
signatures/manifest.json
```

The generated `.crp` is for layout checks only. A real import still needs a
valid trust root, signature threshold, source registration, and downgrade
checks.
