# Releases and downloads

[中文](release.md) · [English home](../README.en.md) · [Maintenance guide](handoff.en.md)

## Install game content

Download the runtime and optional animation examples from the repository home page. Extract them, place the `MechanicalVisualFramework` and `RMVFExamples` folders in the game's `Mods` directory, and load Core, framework and examples in that order.

The framework supports RimWorld 1.6 and 1.7. Players need the game and the dependencies of the mods they use.

## Get the authoring files

Use GitHub's **Code → Download ZIP** to get the full project. Extract it before reading tutorials, editing models or running the toolbox. The shield modeling case is in `Modeling/ShieldGenerator`.

`Downloads/` provides installable runtime and example packages and SHA-256 checksums for those two files. Download the repository for the full development materials. The local packaging tool also generates a `DeveloperKit.zip`.

## Maintain release packages

Complete the checks in the [maintenance guide](handoff.en.md), then run from the repository root:

```text
python Tools/package.py
```

The tool creates runtime, example and full developer packages under `Releases/`. Each ZIP includes a file checksum manifest; a separate SHA-256 list covers all three archives.

The framework version is recorded in `project.json`'s `version`. Documentation, reference assets, explanatory text and cover art use a separate `revision`, included in package names; the current revision is `workshop1`. Preserve previously delivered archives and use new filenames for a new revision.

For Steam Workshop uploads, use the extracted runtime mod directory. The cover is in `Mod/About/Preview.png`; bilingual descriptions, the title, initial change notes and upload steps are in [Workshop materials](../Workshop/README.md). That folder is included only in the authoring project. The Workshop listing has not yet been published.
