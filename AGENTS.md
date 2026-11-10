# Mechanical Visual Framework

Author: Grey·Oviin/OpenAI Assisted.
Read README.md, docs/architecture.md and docs/handoff.md before changing implementation.
Work within this repository; game installations and other projects are reference inputs.
Runtime sources and matching assemblies live in Mod. Examples/Mechanisms is an optional game mod.
Modeling contains authoring examples and reference assets, not installed gameplay content.

Runtime dependencies are the corresponding RimWorld Core assemblies. Python tools use the standard library.
Keep native English and ChineseSimplified game translations in sync.
Comments explain coordinates, ownership, version-specific behavior and constraints.
Only model resources and static indices are shared; each instance owns animation state and mutable mesh buffers.
Keep the 1.6 and 1.7 builds separate. Do not mix raw 1.7 engine buffers with compatibility-layer setters.

Budgets: payload 64 MiB, each archive 64 MiB, installed Mod 16 MiB, generated Work output 256 MiB,
and peak new output 400 MiB. Keep at least 10 GiB free on volumes used by the project and temporary files.
Count historical releases separately and preserve them. Use revisioned names for changed deliveries.
Use Tools/validate.py and Tools/package.py. Keep at most two completed game test profiles per version.
Preserve necessary test summaries before removing temporary outputs.
Resolve cleanup paths, check containment and reparse points, and never traverse game links during deletion.
Exclude ToolPaths.local.json, Work, game binaries, credentials and player saves from commits and packages.
