# Mechanical Visual Framework
Author: Grey·Oviin/OpenAI Assisted. This is an independent reusable framework project.
Read README.md, docs/architecture.md and docs/handoff.md before changing contracts.
Runtime source and matching assemblies live in Mod. Examples are optional consumer mods under Examples.
Do not modify the existing turret experiment, shield project, shared game or workshop sources.
Runtime dependencies: corresponding RimWorld Core assemblies only. Python tools use standard library only.
English and ChineseSimplified native translations are required. Comments explain coordinate, ownership and compatibility contracts.
Only model assets and static indices are shared. Every instance owns mutable animation/mesh state.
Do not silently mix raw 1.7 engine buffers and Unity compatibility setters. Keep two version builds separate.
Current work/payload budget 64 MiB, each archive 64 MiB, Mod installation 16 MiB, Work outputs 256 MiB,
peak new task output 400 MiB; keep C and D at least 10 GiB free. Historical releases are counted separately and never auto-deleted.
Use Tools/validate.py and Tools/package.py. Releases are immutable; Work is disposable after tests finish.
At most two completed test profiles per version. Preserve minimal evidence before removing owned profiles.
Resolve absolute cleanup targets, check containment and reparse points. Never follow a game junction when deleting.
Repository contains portable sources/docs/tools. Exclude ToolPaths.local.json, Work, game DLLs, credentials and player saves.
This applies the local storage policy in the MOD collection's 总项目开发要求 directory; portable budgets above are self-contained.
