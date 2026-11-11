# Versions and releases

[中文](release.md) · [English home](../README.en.md) · [Maintenance guide](handoff.en.md)

## Get a stable release

Use **Code → Download ZIP** on the repository page for the current stable source, runtime resources, models, tools and tutorials. To download an older version, select its version tag in the branch selector first.

For manual installation, copy `Mod` into the game's `Mods` directory and rename it `MechanicalVisualFramework`. Optionally copy `Examples/Mechanisms` and rename it `RMVFExamples`. Load Core, framework and examples in that order.

The Steam Workshop listing has not been published. The following workflow is for maintainers of this framework.

## Local development and public versions

All builds, tests and experiments run locally. GitHub receives only stable releases that have passed local checks, game tests and package-content review. Reusable test scripts belong with the source; logs, saves, temporary images and working notes stay local. Do not run tests in GitHub Actions.

Public versions use `major.minor.patch` with matching Git tags such as `v0.1.0`. Start at `v0.1.0`. Increment the patch for fixes, the minor version for new features, and the major version for incompatible API changes. Public documentation or asset updates also receive a new version; delivered archives are never overwritten.

Stable archive names are:

- `RMVF-v0.1.2-Runtime.zip`
- `RMVF-v0.1.2-Examples.zip`
- `RMVF-v0.1.2-DeveloperKit.zip`

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

Outputs go to the local `Releases` directory. Inspect ZIP contents, file lists and hashes before delivering archives locally. Editable Workshop listing files belong in `Local/Workshop` and are delivered alongside the prepared mod folder. Commit only verified sources, runtime resources, tools, tutorials and examples to GitHub, then create the matching stable tag.

For a local temporary package, use:

```text
python Tools/package.py --label check01
```

Without arguments, the packager uses a timestamp as a local label. The toolbox's Package framework locally option also produces local builds only.
