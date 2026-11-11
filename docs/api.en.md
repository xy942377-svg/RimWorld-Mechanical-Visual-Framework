# Driving visuals from gameplay code

[中文](api.md) · [English home](../README.en.md) · [Model format](model-format.en.md) · [Architecture](architecture.en.md)

A basic display needs only XML: use `Building_MechanicalDisplay` in the ThingDef and add `CompProperties_MechanicalVisual` to `comps`, with a `model` and optional `autoplay`. See [Examples/Mechanisms/Defs/Mechanisms.xml](../Examples/Mechanisms/Defs/Mechanisms.xml). Set `tickerType` to `Normal` and `drawerType` to `RealtimeOnly`. The examples use `rotatable=false`; the model's `yaw` parameter controls facing.

`showControls` defaults to true and exposes model parameters and clips for testing. For a player-facing building, set `<showControls>false</showControls>` in the component XML to hide the generic panel, then drive animation from your own commands or gameplay code.

An existing custom building can retain its gameplay logic and ThingComps. Draw the visual component once. Remove duplicate rendering of the old static graphic or turret head: do not also call vanilla `turretTop.DrawTurret` for the same head or put the animated head into the static map mesh cache. Duplicate rendering can leave a stationary barrel image beneath the moving model. Model `layer` settings control occlusion against map items.

## Common calls

A parameter holds a value such as turn angle or lift height. A clip defines how parameters change over time, such as a recoil motion. An anchor is a named point on the model, such as a muzzle, whose position can be queried for effects or other gameplay code.

```csharp
var visual = building.GetComp<MechanicalVisualFramework.CompMechanicalVisual>();
var animation = visual?.Animation;
animation?.SetTarget("yaw", desiredAngle);       // Turn at the speed set in the model.
animation?.SetTarget("left_elevation", 20f);    // A parameter defined by the example.
animation?.Play("recoil_left");                 // Trigger after gameplay confirms the shot.
```

These names belong to the example model; they are not built-in turret rules. `SetTarget` and `Play` return false for unknown names. `Animation` is null if the asset fails to load. Calling `Play` every tick restarts the clip from time zero. Ordinary target tracking can call `SetTarget` every tick, but this cancels the clip controlling that parameter.

```csharp
UnityEngine.Vector3 position, direction;
if (animation != null &&
    animation.TryAnchor("muzzle_left", building.DrawPos, out position, out direction))
{
    // position uses the same hierarchy transforms and projection as the visible muzzle.
    // Pass it to your firing or effects code; direction is projected onto the map plane.
}
```

## Ownership and saving

`CompMechanicalVisual` owns an independent `VisualInstance` and animator. Model assets, prepared geometry and materials are shared. Pose state, mesh buffers and clip progress belong to each instance. Accessing `Visual` or `Animation` creates resources lazily.

If you create a `VisualInstance` without the component, call `Dispose` when the object is removed or the adapter ends. Reuse the instance across frames. The component releases meshes in `PostDeSpawn` and restores state when spawned again.

Parameters save their current and target values by name. Clips save their name, playback time and paused state. Reordering source nodes or parameters therefore does not restore values into unrelated array indices. Removed names are ignored. If a name's meaning changes, the mod author must decide how to migrate it. Model meshes are not stored in saves.

Only game ticks advance animation. `PostDraw` projects and draws; it does not advance time or calculate damage, power generation or hits. Custom hosts that drive animation manually must follow the same rule so frame rate does not change gameplay results.

## Integration boundaries

This version has no general inverse aiming solver. A map target angle cannot always be used directly as a model's `yaw` under the tilted projection. An elevated muzzle requires your own inverse projection handling. `TryAnchor` provides a visual attachment point, not a collider or a 3D trajectory simulation. Adapters for rotating building bases, moving vehicles and faction colors belong to the mod using the framework.

Public arrays are for reading. Change animation state through methods such as `SetTarget` and `Play`. Model assets are shared by multiple instances and must remain read-only.
