# Maintenance guide

[中文](handoff.md) · [English home](../README.en.md) · [Local verification](verification.en.md) · [Versions and releases](release.en.md)

This guide covers local rebuilding, testing and resource maintenance. The project version is in `project.json`. Before changing implementation, read [architecture](architecture.en.md), [model format](model-format.en.md) and [API](api.en.md).

## Configure the environment

Download the full project. Model authoring requires Python 3.10+. C# changes require Roslyn's `csc.exe` and matching RimWorld installations. Enter tool paths through Configure paths in `Start.cmd`, or copy `ToolPaths.example.json` to `ToolPaths.local.json` and edit it. This configuration stays local.

The builder uses assemblies from `RimWorldWin64_Data/Managed` for 1.6 and the game root for 1.7. When game updates change layouts or APIs, inspect the actual installation and build each version separately.

## Build and test

Run Build sample assets, Build framework DLLs and Validate in the toolbox. Validate checks resources and source/build correspondence, then runs the Python tool tests.

Automated game tests:

```text
powershell -File Tools/Start-Examples.ps1 -Version 1.6 -AutoTest -Launch
powershell -File Tools/Start-Examples.ps1 -Version 1.7 -AutoTest -Launch
```

Run these commands sequentially, waiting for the first game process to exit before starting the next. The launcher uses game links under `Work/Runtime` and separate profiles under `Work/Runs`, leaving normal game settings unchanged. Each run writes `results.txt` to its own directory and exits when complete.

For manual model and control-panel inspection, run:

```text
powershell -File Tools/Start-Examples.ps1 -Version 1.7 -Launch
```

`Mod/BuildManifest.json` records matching sources and DLLs. Rebuild changed models, textures or geometry and verify their BuildHashes. Inspect actual game rendering after renderer changes; numeric checks do not replace visual inspection.

## Implementation rules

- Gameplay drives visuals through parameters, clips and anchors. Firing, energy and navigation belong to the consuming mod.
- Resource paths belong to the mod declaring the model. Share only immutable assets; each instance owns animation state and mesh buffers.
- Do not mix 1.7 native buffers with Unity compatibility setters.
- When model formats or parameter meanings change, check whether saved names and values remain valid.
- Comments explain coordinates, resource ownership, version differences and constraints that must be preserved.

## Local files and publication

Keep test runs, logs and working notes under `Work` or `Local`; they are excluded from the repository and packages. Public versions and local build labels are separate. See [versions and releases](release.en.md) for checks, naming and upload order.

`Work/Runtime` contains links to the game; cleanup must not recurse through those links. Keep at most two completed test runs per game version. Preserve needed results before removing old test profiles. Retain delivered archives under `Releases` without overwriting or deleting them. Size budgets are in `AGENTS.md`.
