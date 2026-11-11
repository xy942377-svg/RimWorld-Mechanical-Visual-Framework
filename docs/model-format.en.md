# Model, coordinate and animation format

[中文](model-format.md) · [English home](../README.en.md) · [Quick start](quickstart.en.md) · [API](api.en.md)

Source files use UTF-8 JSON with top-level `version=1`; compiled model XML also declares `version=1`. See [Templates/model.json](../Templates/model.json) for a complete minimal model. Keep source models in version control. Derived assets can be rebuilt with `Tools/assets.py`.

## Coordinates and hierarchy

Model X points right, Y points back and Z points up. One unit equals one map cell. The neutral facing direction is -Y. The top-level `camera` value sets this model's viewing elevation: default 55°, allowed range 15°–85°. Larger values approach a top-down view; smaller values approach a side view. Rebuild assets and restart the game after changing it.

List parents before their children. A node's `position` is its origin in parent space; `rotation` is a unit quaternion `[x,y,z,w]`; `scale` is positive and uniform. Geometry centers and vertices are in node-local space. A node can have no mesh and act solely as a pivot. The complete model must contain at least one non-degenerate triangle. Write scale as a single number, default 1. The layer defaults to raised; use foundation for a ground-level base.

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
| `palette` | 1–16 RGB rows of integers from 0 to 255; missing rows use the default palette. Materials use entries 0–14; the compiler fixes entry 15 at outline color [19,23,27]. |

A node's `rotation` is a quaternion. Parameters used by `kind="rotation"` bindings use degrees; translation parameters use map cells. A scale binding multiplies node scale by `1 + parameter × factor`, which must stay above 0.001 across the full parameter range. A wrapped parameter must span exactly 360°; target tracking follows the shortest angular difference.

`speed` applies only to movement toward target values. Playing clips follow their keyframe times and values independently of `speed`.

For cylinder geometry, axis is 0, 1 or 2 for X, Y or Z. A binding uses a three-component axis vector, such as [0,0,1] for Z. Rotation uses only its direction; translation also uses its length. Uniform scaling does not use the axis direction.

Keyframe times must increase strictly. Values interpolate linearly, hold the first value before the first key and hold the last value after the last key. A looping clip restarts at `duration`. To make a smooth full rotation, the examples use a continuous 0→360 value track.

Only one clip can control a parameter at a time. `Play` stops existing clips whose parameters overlap with the new clip. Clips with separate parameters can run concurrently. `SetTarget` stops the clip controlling that parameter. `PauseAll` pauses clip tracks while ordinary parameters can still move toward their targets; pausing the game stops both. `StopAll` holds the current pose.

## Compiled assets

`MechanicalModelDef.assetPath` is relative to **the mod declaring that definition**. The game reads `model.xml`, `geometry.bin` and a palette under `Textures`. Mods using the framework must use distinct definition names, package IDs and texture paths.

The compiler generates only those runtime resources by default. To record source and output checksums, append `--hashes Work/MyModelHashes.json` to the build command and keep the record in your development directory. The game does not use it. Bundled example records are stored in `Verification/AssetHashes/`.

`geometry.bin` is little-endian. Its header contains an int32 magic value `0x31564D52` and an int32 triangle count. Each triangle contains an int32 node index, an int32 material index and nine float32 vertex components: 44 bytes in total. Vertex winding determines the outward normal used for shading and outlines. Drawing both sides does not correct bad winding.

Input limits are 256 nodes, 256 parameters and 50,000 triangles. These are format limits, not recommended performance budgets. Each model uses one shared material; each instance has two mutable meshes. Loaded `ModelAsset` arrays are shared across instances and must remain read-only.
