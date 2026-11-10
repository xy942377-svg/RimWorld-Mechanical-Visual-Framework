# RimWorld Mechanical Visual Framework

[中文首页](README.md) · [Quick start](docs/quickstart.md) · [Runtime API](docs/api.md)

Version **0.1.0-candidate1**, RimWorld **1.6 / 1.7**. Author: Grey·Oviin/OpenAI Assisted.

A reusable rigid-part visual system: hierarchical pivots, continuous traversal, elevation, recoil, folding, translation, uniform scale and parameter-driven clips. Model vertices are projected into RimWorld's map plane with flat shading and thick outlines. It is not a PNG-per-angle player, and does not run Blender in game.

Install `Mod` and optionally `Examples/Mechanisms` as separate folders under RimWorld/Mods. Load Core, framework, then examples. Build examples under Misc and open Animation controls. The turret is a visual example, without combat behavior.

The repository includes compiled DLLs, matching C# sources, editable JSON models, a rigid GLB subset importer, a new-mod generator, scripts and tests. Double-click `Start.cmd` on Windows. Configure an existing Python 3.10+ executable. Building framework C# additionally requires an existing Roslyn compiler and locally owned game assemblies. Nothing is downloaded or installed by the tools.

Use `Tools/new_project.py` for a standalone XML/data consumer. Use `CompMechanicalVisual.Animation.SetTarget`, `Play` and `TryAnchor` for a custom adapter. See the commented source and Chinese technical guides for exact contracts.

Only Steam Workshop and this GitHub repository are distribution destinations. Workshop upload files are prepared; the listing is not yet published. MIT covers original code/tools/docs/example assets. Game assemblies and player data are excluded. See LICENSE, NOTICE and docs/verification.md.

