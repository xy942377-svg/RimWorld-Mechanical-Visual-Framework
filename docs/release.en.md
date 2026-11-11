# Versions and releases

[中文](release.md) · [English home](../README.en.md) · [Maintenance guide](handoff.en.md)

## Get a stable release

[Downloads](../Downloads/README.md) contains the runtime, optional animation examples and SHA-256 checksums. Use **Code → Download ZIP** on the repository page for source code, models, authoring tools and tutorials.

Extract `MechanicalVisualFramework` and the optional `RMVFExamples` folder into the game's `Mods` directory. Load Core, framework and examples in that order.

The Steam Workshop listing has not been published. Downloads are currently provided through GitHub.

## Local development and public versions

All builds, tests and experiments run locally. GitHub receives only stable releases that have passed local checks, game tests and package-content review. Reusable test scripts belong with the source; logs, saves, temporary images and working notes stay local. Do not run tests in GitHub Actions.

Public versions use `major.minor.patch` with matching Git tags such as `v0.1.0`. Start at `v0.1.0`. Increment the patch for fixes, the minor version for new features, and the major version for incompatible API changes. Public documentation or asset updates also receive a new version; delivered archives are never overwritten.

Stable archive names are:

- `RMVF-v0.1.0-Runtime.zip`
- `RMVF-v0.1.0-Examples.zip`
- `RMVF-v0.1.0-DeveloperKit.zip`

Local builds use separate labels, such as `RMVF-local-check01-Runtime.zip`. These labels do not consume public version numbers and are not uploaded to GitHub.

## Local verification and packaging

1. Follow the [maintenance guide](handoff.en.md) to build assets and both DLLs, run tool tests and game tests for 1.6 and 1.7, and inspect the rendered models.
2. Review documents, links, attribution, licenses and the actual files to publish. Synchronize the final version in `project.json`, `FrameworkMod.Version`, documentation and the changelog. Rebuild and retest after changing C#.
3. After the checks pass, set `status` in `project.json` to `Stable`, then run:

```text
python Tools/check_release.py
python Tools/package.py --stable
```

The checker verifies current sources, DLLs, models and local game-test results. It records the checked files in `Local/release-check.json`. Stable packaging compares those files again; changed files require another check.

Outputs go to `Releases`. Inspect ZIP contents, file lists and hashes, then copy the runtime and examples into `Downloads` and update its checksums and download guide. Only then commit to GitHub and create the matching stable tag. Failed or unfinished test builds remain local.

For a local temporary package, use:

```text
python Tools/package.py --label check01
```

Without arguments, the packager uses a timestamp as a local label. The toolbox's Package option also produces local builds only.

## Steam Workshop publication

Upload the mod folder from the runtime package. Its cover is `About/Preview.png`; bilingual text is in [Workshop descriptions](../Workshop/README.md). Use “Initial Release” for the first change note.

After publication, inspect the actual image, title, lists and links before adding the Workshop URL to the repository home page. The runtime retains C# source, the license and its user guide. Authoring tools, modeling cases and test tools are supplied with the full GitHub project.
