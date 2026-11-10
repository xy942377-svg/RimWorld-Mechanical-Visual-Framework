# Maintenance guide

[中文](handoff.md) · [English home](../README.en.md) · [Status](status.en.md) · [Verification](verification.en.md) · [Releases](release.en.md)

The framework version is 0.1.0-candidate1; the documentation revision is docs3 (2026-11-10). Start with the repository README. Version and publication status are recorded in `project.json` and [status](status.en.md). Before changing implementation, read [architecture](architecture.en.md), [model format](model-format.en.md) and [API](api.en.md).

This revision adds English versions of all eight detailed guides and reviews project documents, game descriptions, tool prompts, templates and source comments. Error messages now explain the relevant conditions. Runtime algorithms, dependencies and save fields are unchanged.

## Set up the environment

Download the full repository. Precompiled examples need no development software. Model authoring requires an existing Python 3.10+ installation. C# changes require an existing Roslyn `csc.exe` and your own installations of the corresponding RimWorld versions. Copy `ToolPaths.example.json` to `ToolPaths.local.json`, or use **Configure paths** in `Start.cmd`, and enter your local paths.

Build in this order: `BuildAssets → BuildCode → Validate`. Then run `Test16` and `Test17` sequentially. These are actions in `Tools/Toolbox.ps1`, also available through `Start.cmd`. The test launcher uses file links to your game under `Work/Runtime` and separate saves under `Work/Runs`; it leaves your normal ModsConfig unchanged. Run one game version at a time. Automated tests exit when complete.

For manual testing, run this from the repository root:

```text
powershell -File Tools/Start-Examples.ps1 -Version 1.7 -Launch
```

Add `-AutoTest` for automated tests. Use `-Version 1.6` to select the other supported version.

The C# builder targets the verified assembly layouts: the `Managed` subdirectory for 1.6 and the game root for 1.7. If a game update changes assemblies or APIs, inspect the installed version and rebuild against it. DLLs from the two versions are not interchangeable.

## Interface conventions

- Gameplay controls visuals through parameters, clips and anchors. Drawing and asset loading handle display and resources.
- The mod using the framework implements firing, energy and navigation.
- Resource paths belong to the consuming mod. Avoid hard-coded framework roots or global variables tied to a single model.
- Share immutable assets only. Each instance owns its animation state and mesh buffers.
- Update the format `version` when changing the model format, and check whether saved parameter names still have the same meaning. Edit pivots and geometry in source models, then rebuild.
- Do not mix 1.7 native buffers with Unity compatibility setters.
- Rebuild changes to geometry or textures and verify them through `BuildHashes` and `BuildManifest`.
- Keep coordinate, outline and geometry explanations beside the relevant source. Tool behavior is described at the top of each script and in the [quick start](quickstart.en.md).

## Verification and delivery

`Tools/validate.py` checks XML, language keys, geometry, build hashes and size budgets. `Verification/test_tools.py` covers project generation, input limits, reproducible builds and GLB coordinate and hierarchy conversion. `FrameworkProbe.cs` checks transforms, independent joints, playback state, Scribe restoration and tick-driven animation in the real game. Rendering changes also need visual inspection in-game.

`Mod/BuildManifest.json` links source hashes to the DLLs. The tested scope for each version is recorded in [verification](verification.en.md). Link or documentation edits do not require repeating mechanical motion tests. Changed C# sources must be rebuilt and their hashes checked.

Use the whitelist in `Tools/package.py` for packaging. Preserve delivered ZIPs in `Releases`. For framework version changes, update `project.json`, `FrameworkMod.Version` and `CHANGELOG`. For documentation, explanatory text or modeling reference revisions, update `project.json`'s `revision` and `CHANGELOG` while retaining the framework version. `Downloads` contains installable versioned ZIPs; GitHub's **Code → Download ZIP** provides the complete project. Steam uploads use the extracted runtime package. `Modeling` belongs to the developer kit, not the runtime or animation example packages.

To rebuild the shield modeling case:

```text
python Modeling/ShieldGenerator/build_model.py --output Work/ShieldModel
```

This exports OBJ files, materials and structural checks using Python's standard library. See the [case guide](../Modeling/ShieldGenerator/README.en.md) for sprite production.

Do not recursively delete runtime links in `Work` as if they were ordinary directories. Before cleanup, resolve absolute paths, confirm they are inside the project's `Work` folder and check for links. Preserve necessary evidence, then remove completed `Runs` subdirectories that contain no links. Keep at most two completed test runs per game version. Storage budgets are in [AGENTS.md](../AGENTS.md).
