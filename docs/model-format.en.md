# Model, coordinate and animation format

[中文](model-format.md) · [English home](../README.en.md) · [Quick start](quickstart.en.md) · [API](api.en.md)

Source files use UTF-8 JSON with top-level `version=1`; compiled model XML also declares `version=1`. See [Templates/model.json](../Templates/model.json) for a complete minimal model. Keep source models in version control. Derived assets can be rebuilt with `Tools/assets.py`.

## Coordinates and hierarchy

Model X points right, Y points back and Z points up. One unit equals one map cell. The neutral facing direction is -Y, and the default camera elevation is 55°.

List parents before their children. A node's `position` is its origin in parent space; `rotation` is a unit quaternion `[x,y,z,w]`; `scale` is positive and uniform. Geometry centers and vertices are in node-local space. A node can have no mesh and act solely as a pivot. The complete model must contain at least one non-degenerate triangle.

Each pose applies the node's rest rotation, then adds rotations in `bindings` order. Translation offsets follow the **local axes after rotation**, so recoil follows an elevated barrel. To translate before rotating, or to use several different pivots, add intermediate parent nodes.

Child world transforms are:

- `position = parent position + parent rotation × (child local position × parent scale)`
- `rotation = parent rotation × child rotation`
- `scale = parent scale × child scale`

Projection uses `screen horizontal = X` and `map longitudinal = Y·sin(camera) + Z·cos(camera)`.

The rendering Y coordinate in Unity and the compatibility API is used only for depth ordering:

`base altitude + layer altitude band + (-Y·cos(camera) + Z·sin(camera))×0.02`

The `foundation` layer uses the Building altitude band; `raised` is above ItemImportant. These bands control map occlusion, not 3D collision. Check tall or large models in-game against pawns, loose items and other buildings.

## Data fields

| Field | Contents |
|---|---|
| `camera` | Authored orthographic viewing elevation, 15°–85°, default 55°; rebuild and restart after editing |
| `nodes` | `name`, optional `parent`, `position`, `rotation`, `scale`, `layer`, `geometry` |
| `geometry` | `box(center,size)`, `cylinder(center,radius,length,axis,segments)`, or `triangles`; each item has `material=0..14` |
| `parameters` | `name`, `min`, `max`, `default`, `speed`, `wrap`; speed is in parameter units per second, and 0 moves directly to the target |
| `bindings` | `node`, `parameter`, `kind` (`rotation`, `translation` or `scale`), `axis`, `factor` |
| `clips` | `name`, `duration` in seconds, `loop`, `tracks`; each track names a `parameter` and lists `keys` as `[time,value]` pairs |
| `anchors` | `name`, `node`, `position`, `direction`; the default direction is -Y |
| `palette` | Up to 16 RGB byte-color rows; entries 0..14 are materials and entry 15 is reserved for dark outlines |

Rotation uses degrees; translation uses map cells. A scale binding multiplies node scale by `1 + parameter × factor`, which must remain positive. A wrapped parameter must span exactly 360°; target tracking follows the shortest angular difference.

Keyframe times must increase strictly. Values interpolate linearly, hold the first value before the first key and hold the last value after the last key. A looping clip restarts at `duration`. To make a smooth full rotation, the examples use a continuous 0→360 value track.

Only one clip can control a parameter at a time. `Play` stops existing clips whose parameters overlap with the new clip. Clips with separate parameters can run concurrently. `SetTarget` stops the clip controlling that parameter. `PauseAll` pauses clip tracks while ordinary parameters can still move toward their targets; pausing the game stops both. `StopAll` holds the current pose.

## Compiled assets

`MechanicalModelDef.assetPath` is relative to **the mod declaring that definition**. Each model has `model.xml`, `geometry.bin` and `BuildHashes.json`; its palette uses a globally unique `Textures` path. Mods using the framework must use distinct definition names, package IDs and texture paths.

`geometry.bin` is little-endian. Its header contains an int32 magic value `0x31564D52` and an int32 triangle count. Each triangle contains an int32 node index, an int32 material index and nine float32 vertex components: 44 bytes in total. Vertex winding determines the outward normal used for shading and outlines. Drawing both sides does not correct bad winding.

Input limits are 256 nodes, 256 parameters and 50,000 triangles. These are format limits, not recommended performance budgets. Each model uses one shared material; each instance has two mutable meshes. Loaded `ModelAsset` arrays are shared across instances and must remain read-only.
