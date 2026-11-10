# Verification record

[中文](verification.md) · [English home](../README.en.md) · [Maintenance guide](handoff.en.md)

## Framework 0.1.0-candidate1

Tests ran on 2026-11-10 on Windows with RimWorld 1.6.4871 and 1.7.5000. Enabled content was Core, the framework, animation examples and the FrameworkProbe test component.

Passed checks:

- Pivots, parent-child rotations, barrel elevation and recoil along a rotated local axis.
- Mesh updates after anchor queries: 0 updated nodes for an unchanged pose, 1 for single-barrel recoil and 4 active nodes for overall turret rotation.
- Independent instance state, concurrent clips using separate parameters and parameter conflict handling.
- Target speed, the shortest turn from 359° to 1°, clip looping, pausing and stopping.
- Scribe saving and restoration of current and target parameter values, clip time and paused state.
- Pose restoration and recreation of independent meshes when a building is despawned and spawned again.
- Three different models running together, with at least 10 normal game ticks advancing animation in each version.
- Eight Python tool tests covering template generation, reproducible builds, input checks and GLB coordinate and hierarchy conversion.

Visual inspection covered models in 1.7 and models plus the animation control panel in 1.6. The 1.6 in-game check used the final DLL. After the 1.7 mechanical tests, only link constants, comments and error messages changed before recompilation. Summaries and representative screenshots are in `Verification/Evidence/`.

The full developer package was also rebuilt in an independent directory: all three models and both DLLs matched the packaged files. See `Verification/Evidence/cold-rebuild.txt`.

Complete-save migration between game versions, hardware performance benchmarks and complex mod combinations have not been tested. GLB importer tests use synthetic files; accepted input is described in the [quick start](quickstart.en.md#4-import-from-modeling-software).

## Documentation revision docs2

Checks covered wording and bilingual content, download and documentation links, template generation, shield model export, source-to-DLL correspondence, package manifests and archive integrity. Every valid triangle in the three shield OBJ exports was compared with the original model; vertices and materials matched. The maximum coordinate error after reversing the four corner transforms was approximately 3.33×10⁻¹⁶. The shield case is an authoring reference and was not tested as a fourth in-game building.

Rebuilt DLLs for both game versions were byte-for-byte identical to those before the documentation revision, and all eight tool tests passed. Animation and rendering algorithms and save fields were unchanged. In-game mechanical motion tests were not repeated for this revision.

## Documentation revision docs3

Added English versions of the eight detailed guides and reviewed project prose, game descriptions, tool prompts, templates, error messages and source comments. Chinese and English commands and C# examples match. Internal links and section anchors were checked. A new mod was generated to inspect its bilingual guide; the build command in that guide also ran successfully with spaces in the mod path.

Both DLLs were rebuilt because runtime error messages changed, and source-to-assembly hash checks passed. Comparison confirmed that executable C# logic was unchanged. All eight Python tool tests and PowerShell syntax checks passed. Models and textures were unchanged; in-game animation tests were not repeated for this revision.
