# Local verification scope

[中文](verification.md) · [English home](../README.en.md) · [Maintenance guide](handoff.en.md)

Version: **v0.1.1**. Verified on 2026-11-11 on Windows with RimWorld 1.6.4871 and 1.7.5000. Enabled content was Core, the framework, mechanical examples and the local test component.

## Verified behavior

- Part pivots, parent-child rotations, barrel elevation and recoil along a rotated local axis.
- Continuous turning, the shortest turn from 359° to 1°, independent concurrent clips, looping, pausing and stopping.
- Independent instance state. Mesh updates remain correct after anchor queries: 0 updated nodes for an unchanged pose, 1 for single-barrel recoil and 4 active nodes for overall turret rotation.
- Saving and restoring current and target parameter values, clip time and paused state; pose restoration after a building is despawned and spawned again.
- Three examples rendering together, with animation driven by normal game updates. Model views and controls were inspected in both versions; the window adjusts to the available space after interface scaling.
- Eleven tool tests covering template generation, reproducible builds, input validation, GLB coordinates and hierarchy, stable-package verification records, detection of changed files and preservation of existing archives.

The build manifest connects sources to both DLLs. The three examples' geometry, textures and source files are checked against hashes and rebuilt output. Archive checks cover the file list, ZIP integrity and hashes of the packaged files.

## Reproducing the checks

Follow [Build and test](handoff.en.md#build-and-test) for tool checks and both automated game tests. Test tools are included with the source; test runs and results stay local. See [Releases](release.en.md) for stable packaging.

The shield modeling case contains a standalone builder, four rotated copies of one corner model, and separate base and orb exports. It teaches modeling and projection and is not installed as a fourth game building. See the [case guide](../Modeling/ShieldGenerator/README.en.md).

Checks for this version do not cover complete-save migration between game versions, hardware performance benchmarks or complex mod combinations. GLB tests use synthetic models; real input must meet the [import requirements](quickstart.en.md#4-import-from-modeling-software).
