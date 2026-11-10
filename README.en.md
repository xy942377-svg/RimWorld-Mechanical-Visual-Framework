# RimWorld Mechanical Visual Framework

[中文首页](README.md) · [Quick start (Chinese)](docs/quickstart.md) · [API (Chinese)](docs/api.md) · [Shield modeling example](Modeling/ShieldGenerator/README.en.md)

A visual framework for rigid mechanical parts in RimWorld. It supports continuous rotation, independent elevation and recoil, translation, folding and uniform scaling. Each part has a local pivot and can inherit motion from a parent. The renderer projects the current pose onto the map with flat shading and thick outlines.

Framework version: **0.1.0-candidate1**, for RimWorld **1.6 / 1.7**. Documentation revision **docs2** adds clearer instructions and a shield-generator modeling example. Author: Grey·Oviin/OpenAI Assisted.

## Install and try

Download the [runtime](https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework/blob/main/Downloads/RMVF-0.1.0-candidate1-docs2-Workshop.zip) and optionally the [examples](https://github.com/xy942377-svg/RimWorld-Mechanical-Visual-Framework/blob/main/Downloads/RMVF-0.1.0-candidate1-docs2-Examples.zip). Extract `MechanicalVisualFramework` and `RMVFExamples` into RimWorld's `Mods` folder.

Load **Core → Mechanical Visual Framework → RMVF · Mechanical examples**. The runtime requires Core; the examples require the framework. Build the examples under **Misc** and open **Animation controls**. The triple turret demonstrates rotation, independent gun elevation and recoil; it does not fire projectiles.

The Steam Workshop listing is not published yet. Downloads are available here.

## Create a model

Use **Code → Download ZIP** for the full project, then extract it. On Windows, run `Start.cmd`, select **Configure paths** and enter an existing Python 3.10+ executable. Select **New mod** to create a working model-based mod. Framework C# changes also require Roslyn and the matching local game assemblies.

The project includes editable JSON models, a GLB importer for supported rigid-node files, templates, build scripts and tests. The optional shield modeling example demonstrates four rotated copies of one shared corner, a separate sphere, OBJ export and aligned PNG layers.

The runtime supports parameter-driven rotation, translation and uniform scaling, linear keyframes, concurrent clips with separate parameters, visual anchors and saved animation state. Gameplay such as firing, power generation and shield interception belongs to the mod using the framework. Skinning, flexible deformation and inverse kinematics are not implemented. The GLB importer supports rigid geometry and plain opaque colors; its accepted input is documented in the quick start.

Game controls are available in English and Simplified Chinese. The toolbox uses English; detailed API and format guides are currently in Chinese.

## License and testing

Original code, tools, documentation and examples use [MIT](LICENSE). See [NOTICE](NOTICE.md) for attribution and [verification](docs/verification.md) for tested versions and scope.
