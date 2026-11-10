# Runtime responsibilities and performance

[中文](architecture.md) · [English home](../README.en.md) · [API](api.en.md) · [Maintenance guide](handoff.en.md)

`Asset.cs` reads resources from the mod declaring the model, validates the format and caches one read-only asset per `MechanicalModelDef`. `PreparedGeometry.cs` merges duplicate vertices, calculates normals and builds candidate outline edges during loading.

`Animation.cs` computes local transforms from parameters, then processes parents before children. Each node has a pose revision number. Querying an anchor does not clear the update information needed by the renderer. `VisualInstance.cs` compares revision numbers and updates only parts whose poses changed. It reuses normals and facing results when rotation is unchanged, and reuses existing geometry for stationary models.

`MeshBuffers.cs` handles Unity buffers in 1.6 and Waylith buffers in 1.7 separately. Once 1.7 uses native `CpuMeshData`, subsequent updates must use that buffer. Mixing it with compatibility-layer `vertices`, `uv`, `triangles` setters or `Clear` can copy arrays or change buffer state. Both versions use the same projection and outline rules, with separate builds and tests in their corresponding game versions.

Each instance draws two meshes: surfaces and visible outlines. Vertex and index arrays are allocated to capacity in advance, with active outline indices packed contiguously. Outline half-width is 0.035 cells; crease half-width is 0.018 cells. Material palettes provide 32 brightness levels. Triangle count, outline edges, active parts and visible instance count all affect cost.

The framework handles models, animation, rendering and saving. The mod using it implements gameplay rules. Authoring tools run during development; players do not need Python or modeling software.

Functional checks have covered three different models running together. Multi-instance performance benchmarks have not yet been run. When measuring, record time and memory for stationary models, one moving joint, whole-model rotation, and 10 or 50 visible instances. Include the game version, model triangle count and rendering backend.
